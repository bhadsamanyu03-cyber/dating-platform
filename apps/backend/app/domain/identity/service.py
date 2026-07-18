import json
import uuid
from datetime import timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings
from app.domain.identity.models import (
    AuditLog,
    EmailVerificationToken,
    PasswordResetToken,
    RefreshSession,
    User,
)
from app.domain.identity.security import (
    create_jwt,
    decode_jwt,
    generate_opaque_token,
    hash_password,
    token_hash,
    utcnow,
    validate_password,
    verify_password,
    InvalidTokenError,
)
from app.infrastructure.email import EmailProvider


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message, self.status_code = message, status_code


class IdentityService:
    def __init__(self, db: AsyncSession, settings: Settings, email_provider: EmailProvider):
        self.db, self.settings, self.email_provider = db, settings, email_provider

    async def audit(
        self, event: str, user_id: uuid.UUID | None, ip: str | None, **metadata: str
    ) -> None:
        self.db.add(
            AuditLog(
                user_id=user_id,
                event=event,
                ip_address=ip,
                metadata_json=json.dumps(metadata) if metadata else None,
            )
        )

    async def register(self, email: str, password: str, ip: str | None) -> User:
        email = email.casefold().strip()
        validate_password(password, email)
        existing = await self.db.scalar(select(User).where(User.email == email))
        if existing:
            raise AuthError("An account with that email already exists", 409)
        user = User(email=email, password_hash=hash_password(password))
        self.db.add(user)
        await self.db.flush()
        await self._send_verification(user, ip)
        await self.audit("user_registered", user.id, ip)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def _send_verification(self, user: User, ip: str | None) -> None:
        await self.db.execute(
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user.id, EmailVerificationToken.used_at.is_(None)
            )
            .values(used_at=utcnow())
        )
        raw = generate_opaque_token()
        self.db.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash(raw),
                expires_at=utcnow() + timedelta(hours=self.settings.email_token_hours),
            )
        )
        await self.email_provider.send(
            user.email, "Verify your email", f"Verification token: {raw}"
        )
        await self.audit("verification_sent", user.id, ip)

    async def resend_verification(self, email: str, ip: str | None) -> None:
        user = await self.db.scalar(
            select(User).where(User.email == email.casefold().strip(), User.is_active.is_(True))
        )
        if user and not user.is_email_verified:
            await self._send_verification(user, ip)
            await self.db.commit()

    async def verify_email(self, raw: str, ip: str | None) -> None:
        record = await self.db.scalar(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash(raw),
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > utcnow(),
            )
        )
        if not record:
            raise AuthError("Verification token is invalid or expired", 400)
        user = await self.db.get(User, record.user_id)
        record.used_at, user.is_email_verified = utcnow(), True
        await self.audit("email_verified", user.id, ip)
        await self.db.commit()

    async def login(
        self, email: str, password: str, ip: str | None, user_agent: str | None
    ) -> tuple[User, dict]:
        user = await self.db.scalar(select(User).where(User.email == email.casefold().strip()))
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            await self.audit("login_failed", user.id if user else None, ip)
            await self.db.commit()
            raise AuthError("Invalid email or password", 401)
        if not user.is_email_verified:
            raise AuthError("Email verification is required", 403)
        tokens = await self._create_session_tokens(user, ip, user_agent)
        await self.audit("login_succeeded", user.id, ip)
        await self.db.commit()
        return user, tokens

    async def _create_session_tokens(
        self, user: User, ip: str | None, user_agent: str | None, family_id: uuid.UUID | None = None
    ) -> dict:
        session = RefreshSession(
            user_id=user.id,
            family_id=family_id or uuid.uuid4(),
            token_hash="pending",
            expires_at=utcnow() + timedelta(days=self.settings.refresh_token_days),
            ip_address=ip,
            user_agent=(user_agent or "")[:512] or None,
        )
        self.db.add(session)
        await self.db.flush()
        refresh = create_jwt(
            self.settings.jwt_secret_key.get_secret_value(),
            user.id,
            "refresh",
            timedelta(days=self.settings.refresh_token_days),
            user.credential_version,
            session.id,
        )
        session.token_hash = token_hash(refresh)
        access = create_jwt(
            self.settings.jwt_secret_key.get_secret_value(),
            user.id,
            "access",
            timedelta(minutes=self.settings.access_token_minutes),
            user.credential_version,
            session.id,
        )
        return {
            "access_token": access,
            "refresh_token": refresh,
            "expires_in": self.settings.access_token_minutes * 60,
        }

    async def refresh(self, raw: str, ip: str | None, user_agent: str | None) -> dict:
        claims = decode_jwt(raw, self.settings.jwt_secret_key.get_secret_value(), "refresh")
        session = await self.db.get(RefreshSession, uuid.UUID(claims["sid"]))
        if not session or session.token_hash != token_hash(raw) or session.expires_at <= utcnow():
            raise AuthError("Invalid refresh token", 401)
        if session.revoked_at:
            await self.db.execute(
                update(RefreshSession)
                .where(
                    RefreshSession.family_id == session.family_id,
                    RefreshSession.revoked_at.is_(None),
                )
                .values(revoked_at=utcnow())
            )
            await self.audit("refresh_replay_detected", session.user_id, ip)
            await self.db.commit()
            raise AuthError("Refresh token replay detected", 401)
        user = await self.db.get(User, session.user_id)
        if not user or not user.is_active or claims["ver"] != user.credential_version:
            raise AuthError("Invalid refresh token", 401)
        session.revoked_at = utcnow()
        tokens = await self._create_session_tokens(user, ip, user_agent, session.family_id)
        new_session_id = uuid.UUID(
            decode_jwt(
                tokens["refresh_token"], self.settings.jwt_secret_key.get_secret_value(), "refresh"
            )["sid"]
        )
        session.replaced_by_id = new_session_id
        await self.audit("token_refreshed", user.id, ip)
        await self.db.commit()
        return tokens

    async def authenticated_user(self, raw: str) -> User:
        claims = decode_jwt(raw, self.settings.jwt_secret_key.get_secret_value(), "access")
        user = await self.db.get(User, uuid.UUID(claims["sub"]))
        if (
            not user
            or not user.is_active
            or user.deleted_at
            or user.credential_version != claims["ver"]
        ):
            raise AuthError("Authentication required", 401)
        return user

    async def logout(self, raw: str, ip: str | None) -> None:
        try:
            claims = decode_jwt(raw, self.settings.jwt_secret_key.get_secret_value(), "refresh")
            session = await self.db.get(RefreshSession, uuid.UUID(claims["sid"]))
            if session and session.token_hash == token_hash(raw) and not session.revoked_at:
                session.revoked_at = utcnow()
                await self.audit("logout", session.user_id, ip)
                await self.db.commit()
        except InvalidTokenError:
            pass

    async def forgot_password(self, email: str, ip: str | None) -> None:
        user = await self.db.scalar(
            select(User).where(User.email == email.casefold().strip(), User.is_active.is_(True))
        )
        if user:
            await self.db.execute(
                update(PasswordResetToken)
                .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
                .values(used_at=utcnow())
            )
            raw = generate_opaque_token()
            self.db.add(
                PasswordResetToken(
                    user_id=user.id,
                    token_hash=token_hash(raw),
                    expires_at=utcnow() + timedelta(minutes=self.settings.password_reset_minutes),
                )
            )
            await self.email_provider.send(
                user.email, "Reset your password", f"Password reset token: {raw}"
            )
            await self.audit("password_reset_requested", user.id, ip)
            await self.db.commit()

    async def set_password_with_token(self, raw: str, password: str, ip: str | None) -> None:
        record = await self.db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash(raw),
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > utcnow(),
            )
        )
        if not record:
            raise AuthError("Password reset token is invalid or expired", 400)
        user = await self.db.get(User, record.user_id)
        validate_password(password, user.email)
        user.password_hash, user.credential_version, record.used_at = (
            hash_password(password),
            user.credential_version + 1,
            utcnow(),
        )
        await self._revoke_user_sessions(user.id)
        await self.audit("password_reset_completed", user.id, ip)
        await self.db.commit()

    async def change_password(self, user: User, current: str, new: str, ip: str | None) -> None:
        if not verify_password(current, user.password_hash):
            raise AuthError("Current password is incorrect", 400)
        validate_password(new, user.email)
        user.password_hash, user.credential_version = (
            hash_password(new),
            user.credential_version + 1,
        )
        await self._revoke_user_sessions(user.id)
        await self.audit("password_changed", user.id, ip)
        await self.db.commit()

    async def _revoke_user_sessions(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(RefreshSession)
            .where(RefreshSession.user_id == user_id, RefreshSession.revoked_at.is_(None))
            .values(revoked_at=utcnow())
        )

    async def sessions(self, user: User, current_session_id: str | None) -> list[RefreshSession]:
        rows = await self.db.scalars(
            select(RefreshSession)
            .where(RefreshSession.user_id == user.id, RefreshSession.revoked_at.is_(None))
            .order_by(RefreshSession.created_at.desc())
        )
        return list(rows)

    async def revoke_session(self, user: User, session_id: uuid.UUID, ip: str | None) -> None:
        session = await self.db.scalar(
            select(RefreshSession).where(
                RefreshSession.id == session_id, RefreshSession.user_id == user.id
            )
        )
        if not session:
            raise AuthError("Session not found", 404)
        session.revoked_at = utcnow()
        await self.audit("session_revoked", user.id, ip, session_id=str(session_id))
        await self.db.commit()

    async def delete_account(self, user: User, password: str, ip: str | None) -> None:
        if not verify_password(password, user.password_hash):
            raise AuthError("Password is incorrect", 400)
        user.is_active, user.deleted_at, user.credential_version = (
            False,
            utcnow(),
            user.credential_version + 1,
        )
        await self._revoke_user_sessions(user.id)
        await self.audit("account_soft_deleted", user.id, ip)
        await self.db.commit()
