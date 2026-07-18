from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.messaging.models import Message
from app.domain.messaging.repository import MessagingRepository
from app.domain.messaging.schemas import (
    ConversationPage,
    ConversationResponse,
    MessageCreate,
    MessagePage,
    MessageResponse,
)


class MessagingError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status_code = message, status


class MessagingService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, MessagingRepository(db)

    async def ensure_conversation(self, match_id: UUID):
        return await self.repo.ensure_conversation(match_id)

    async def conversation(self, conversation_id: UUID, user_id: UUID):
        value = await self.repo.conversation_for_user(conversation_id, user_id)
        if not value:
            raise MessagingError("Conversation not found", 404)
        return value

    async def list(self, user_id: UUID):
        return ConversationPage(
            conversations=[
                ConversationResponse(id=x.id, match_id=x.match_id, created_at=x.created_at)
                for x in await self.repo.list_for_user(user_id, 50)
            ],
            next_cursor=None,
        )

    async def send(self, conversation_id: UUID, user_id: UUID, payload: MessageCreate):
        await self.conversation(conversation_id, user_id)
        if payload.message_type in {"IMAGE", "VIDEO"}:
            asset = await self.repo.media(payload.media_asset_id, user_id)
            if not asset or asset.media_type != payload.message_type:
                raise MessagingError("Invalid media asset", 422)
        message = Message(
            conversation_id=conversation_id,
            sender_user_id=user_id,
            message_type=payload.message_type,
            text_content=payload.text_content,
            media_asset_id=payload.media_asset_id,
        )
        await self.repo.add_message(message)
        await self.db.commit()
        await self.db.refresh(message)
        return self.message_response(message)

    def message_response(self, value):
        return MessageResponse(
            id=value.id,
            sender_user_id=value.sender_user_id,
            message_type=value.message_type,
            text_content=value.text_content,
            media_asset_id=value.media_asset_id,
            created_at=value.created_at,
        )

    async def messages(self, conversation_id: UUID, user_id: UUID):
        await self.conversation(conversation_id, user_id)
        return MessagePage(
            messages=[
                self.message_response(x) for x in await self.repo.messages(conversation_id, 50)
            ],
            next_cursor=None,
        )
