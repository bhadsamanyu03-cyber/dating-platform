from datetime import UTC, datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_database_session
from app.core.config import get_settings
from app.domain.identity.models import User
from app.domain.identity.schemas import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    OpaqueTokenRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SessionResponse,
    TokenResponse,
    UserResponse,
)
from app.domain.identity.service import AuthError, IdentityService

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)


def requester_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def auth_service(
    request: Request, db: AsyncSession = Depends(get_database_session)
) -> IdentityService:
    return IdentityService(db, get_settings(), request.app.state.email_provider)


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    service: IdentityService = Depends(auth_service),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await service.authenticated_user(credentials.credentials)
    except AuthError as exc:
        raise HTTPException(
            status_code=exc.status_code, detail=exc.message, headers={"WWW-Authenticate": "Bearer"}
        ) from exc


def current_session_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UUID | None:
    if not credentials:
        return None
    from app.domain.identity.security import InvalidTokenError, decode_jwt

    try:
        claims = decode_jwt(
            credentials.credentials, get_settings().jwt_secret_key.get_secret_value(), "access"
        )
        return UUID(claims["sid"])
    except (InvalidTokenError, KeyError, ValueError):
        return None


async def rate_limit(request: Request) -> None:
    settings = get_settings()
    key = f"rate:auth:{requester_ip(request)}:{datetime.now(UTC).strftime('%Y%m%d%H%M')}"
    count = await request.app.state.redis.incr(key)
    if count == 1:
        await request.app.state.redis.expire(key, 60)
    if count > settings.auth_rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Too many requests; try again later")


def user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit)],
)
async def register(
    payload: RegisterRequest, request: Request, service: IdentityService = Depends(auth_service)
) -> UserResponse:
    try:
        return user_response(
            await service.register(str(payload.email), payload.password, requester_ip(request))
        )
    except (AuthError, ValueError) as exc:
        raise HTTPException(
            status_code=exc.status_code if isinstance(exc, AuthError) else 422,
            detail=exc.message if isinstance(exc, AuthError) else str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit)])
async def login(
    payload: LoginRequest, request: Request, service: IdentityService = Depends(auth_service)
) -> TokenResponse:
    try:
        _, tokens = await service.login(
            str(payload.email),
            payload.password,
            requester_ip(request),
            request.headers.get("user-agent"),
        )
        return TokenResponse(**tokens)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/logout", status_code=204)
async def logout(
    payload: RefreshRequest, request: Request, service: IdentityService = Depends(auth_service)
) -> Response:
    await service.logout(payload.refresh_token, requester_ip(request))
    return Response(status_code=204)


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(rate_limit)])
async def refresh(
    payload: RefreshRequest, request: Request, service: IdentityService = Depends(auth_service)
) -> TokenResponse:
    try:
        return TokenResponse(
            **await service.refresh(
                payload.refresh_token, requester_ip(request), request.headers.get("user-agent")
            )
        )
    except (AuthError, Exception) as exc:
        if isinstance(exc, AuthError):
            raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc


@router.post("/verify-email", status_code=204)
async def verify_email(
    payload: OpaqueTokenRequest, request: Request, service: IdentityService = Depends(auth_service)
) -> Response:
    try:
        await service.verify_email(payload.token, requester_ip(request))
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return Response(status_code=204)


@router.post("/resend-verification", status_code=202, dependencies=[Depends(rate_limit)])
async def resend_verification(
    payload: ForgotPasswordRequest,
    request: Request,
    service: IdentityService = Depends(auth_service),
) -> Response:
    await service.resend_verification(str(payload.email), requester_ip(request))
    return Response(status_code=202)


@router.post("/forgot-password", status_code=202, dependencies=[Depends(rate_limit)])
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    service: IdentityService = Depends(auth_service),
) -> Response:
    await service.forgot_password(str(payload.email), requester_ip(request))
    return Response(status_code=202)


@router.post("/reset-password", status_code=204)
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    service: IdentityService = Depends(auth_service),
) -> Response:
    try:
        await service.set_password_with_token(
            payload.token, payload.password, requester_ip(request)
        )
    except (AuthError, ValueError) as exc:
        raise HTTPException(
            status_code=exc.status_code if isinstance(exc, AuthError) else 422,
            detail=exc.message if isinstance(exc, AuthError) else str(exc),
        ) from exc
    return Response(status_code=204)


@router.post("/change-password", status_code=204)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user: User = Depends(current_user),
    service: IdentityService = Depends(auth_service),
) -> Response:
    try:
        await service.change_password(
            user, payload.current_password, payload.new_password, requester_ip(request)
        )
    except (AuthError, ValueError) as exc:
        raise HTTPException(
            status_code=exc.status_code if isinstance(exc, AuthError) else 422,
            detail=exc.message if isinstance(exc, AuthError) else str(exc),
        ) from exc
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(current_user)) -> UserResponse:
    return user_response(user)


@router.get("/sessions", response_model=list[SessionResponse])
async def sessions(
    user: User = Depends(current_user),
    session_id: UUID | None = Depends(current_session_id),
    service: IdentityService = Depends(auth_service),
) -> list[SessionResponse]:
    result = await service.sessions(user, str(session_id) if session_id else None)
    return [
        SessionResponse(
            id=s.id,
            user_agent=s.user_agent,
            ip_address=s.ip_address,
            created_at=s.created_at,
            expires_at=s.expires_at,
            current=s.id == session_id,
        )
        for s in result
    ]


@router.delete("/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: UUID,
    request: Request,
    user: User = Depends(current_user),
    service: IdentityService = Depends(auth_service),
) -> Response:
    try:
        await service.revoke_session(user, session_id, requester_ip(request))
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return Response(status_code=204)


@router.delete("/account", status_code=204)
async def delete_account(
    payload: DeleteAccountRequest,
    request: Request,
    user: User = Depends(current_user),
    service: IdentityService = Depends(auth_service),
) -> Response:
    try:
        await service.delete_account(user, payload.password, requester_ip(request))
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return Response(status_code=204)
