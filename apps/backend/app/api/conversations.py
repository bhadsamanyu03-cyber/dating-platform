from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter(prefix="/conversations", tags=["conversations"])


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
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await MessagingService(db).messages(conversation_id, user.id)
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
