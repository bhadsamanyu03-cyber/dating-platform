import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

PASSWORD_HASHER = PasswordHasher()
COMMON_PASSWORDS = {"password", "password123", "12345678", "qwerty123", "letmein123", "welcome123"}


class InvalidTokenError(Exception):
    pass


def utcnow() -> datetime:
    return datetime.now(UTC)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def validate_password(password: str, email: str | None = None) -> None:
    normalized = password.casefold()
    if len(password) < 12 or len(password) > 128:
        raise ValueError("Password must contain 12 to 128 characters")
    if normalized in COMMON_PASSWORDS or (
        email and email.split("@", 1)[0].casefold() in normalized
    ):
        raise ValueError("Password is too common or predictable")
    if not (
        any(c.islower() for c in password)
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
    ):
        raise ValueError("Password must include upper-case, lower-case, and numeric characters")


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash_value: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(password_hash_value, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_jwt(
    secret: str,
    subject: UUID,
    token_type: str,
    expires_in: timedelta,
    version: int,
    session_id: UUID | None = None,
) -> str:
    now = utcnow()
    claims = {
        "sub": str(subject),
        "typ": token_type,
        "iat": now,
        "exp": now + expires_in,
        "jti": str(uuid4()),
        "ver": version,
    }
    if session_id:
        claims["sid"] = str(session_id)
    return jwt.encode(claims, secret, algorithm="HS256")


def decode_jwt(token: str, secret: str, expected_type: str) -> dict:
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "jti", "typ", "ver"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("Invalid or expired token") from exc
    if claims["typ"] != expected_type:
        raise InvalidTokenError("Wrong token type")
    return claims
