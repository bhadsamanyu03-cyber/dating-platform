from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.identity.models import User
from app.domain.messaging.schemas import (
    ConversationPage,
    ConversationResponse,
    MessageCreate,
    MessagePage,
    MessageResponse,
)
from app.domain.messaging.service import MessagingError, MessagingService
from app.domain.media.storage import LocalStorageProvider
from app.core.config import get_settings

router = APIRouter(prefix="/conversations", tags=["conversations"])
message_router = APIRouter(prefix="/messages", tags=["messages"])


def error(value):
    return HTTPException(value.status_code, value.message)


@router.get("", response_model=ConversationPage)
async def list_conversations(
    user: User = Depends(current_user), db: AsyncSession = Depends(get_database_session)
):
    return await MessagingService(db).list(user.id)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        value = await MessagingService(db).conversation(conversation_id, user.id)
        return ConversationResponse(
            id=value.id, match_id=value.match_id, created_at=value.created_at
        )
    except MessagingError as exc:
        raise error(exc) from exc


@router.get("/{conversation_id}/messages", response_model=MessagePage)
async def list_messages(
    conversation_id: UUID,
    cursor: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await MessagingService(db).messages(conversation_id, user.id, cursor, limit)
    except MessagingError as exc:
        raise error(exc) from exc


@message_router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await MessagingService(db).message(message_id, user.id)
    except MessagingError as exc:
        raise error(exc) from exc


@message_router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await MessagingService(db).delete(message_id, user.id)
    except MessagingError as exc:
        raise error(exc) from exc
    return Response(status_code=204)


@message_router.get("/{message_id}/media/{asset_id}")
async def download_attachment(
    message_id: UUID,
    asset_id: UUID,
    variant: str | None = Query(default=None, pattern="^(DISPLAY|THUMBNAIL)$"),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> StreamingResponse:
    try:
        storage_key, mime_type = await MessagingService(db).attachment(
            message_id, asset_id, user.id, variant
        )
        return StreamingResponse(
            LocalStorageProvider(get_settings().media_storage_path).download(storage_key),
            media_type=mime_type,
        )
    except MessagingError as exc:
        raise error(exc) from exc


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    conversation_id: UUID,
    payload: MessageCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await MessagingService(db).send(conversation_id, user.id, payload)
    except MessagingError as exc:
        raise error(exc) from exc
