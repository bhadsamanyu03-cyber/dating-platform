import base64
import binascii
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.messaging.models import Message
from app.domain.messaging.events import MessageImageUploaded
from app.domain.messaging.repository import MessagingRepository
from app.domain.messaging.schemas import (
    ConversationPage,
    ConversationResponse,
    MessageCreate,
    MessagePage,
    MessageResponse,
)


class MessagingError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message, self.status_code = message, status


def encode_cursor(message: Message) -> str:
    return base64.urlsafe_b64encode(
        json.dumps([message.created_at.isoformat(), str(message.id)]).encode()
    ).decode()


def decode_cursor(cursor: str | None) -> tuple[datetime, UUID] | None:
    if not cursor:
        return None
    try:
        timestamp, identifier = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return datetime.fromisoformat(timestamp), UUID(identifier)
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError):
        raise MessagingError("Invalid cursor", 422) from None


class MessagingService:
    def __init__(self, db: AsyncSession):
        self.db, self.repo = db, MessagingRepository(db)
        self.events: list[MessageImageUploaded] = []

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

    def message_response(self, value: Message):
        return MessageResponse(
            id=value.id,
            sender_user_id=value.sender_user_id,
            message_type=value.message_type,
            text_content=value.text_content,
            media_asset_ids=[
                link.media_asset_id for link in sorted(value.media, key=lambda x: x.ordering)
            ],
            created_at=value.created_at,
            delivered_at=value.delivered_at,
            read_at=value.read_at,
            deleted_at=value.deleted_at,
            client_message_id=value.client_message_id,
        )

    async def send(self, conversation_id: UUID, user_id: UUID, payload: MessageCreate):
        await self.conversation(conversation_id, user_id)
        existing = await self.repo.existing_message(user_id, payload.client_message_id)
        if existing:
            if existing.conversation_id != conversation_id:
                raise MessagingError("Client message id conflict", 409)
            return self.message_response(existing)
        assets = await self.repo.media(payload.media_asset_ids, user_id)
        if len(assets) != len(payload.media_asset_ids):
            raise MessagingError("Invalid media asset", 422)
        message = await self.repo.add_message(
            Message(
                conversation_id=conversation_id,
                sender_user_id=user_id,
                message_type="IMAGE" if payload.media_asset_ids else "TEXT",
                text_content=payload.text_content,
                media_asset_id=payload.media_asset_ids[0] if payload.media_asset_ids else None,
                client_message_id=payload.client_message_id,
            ),
            payload.media_asset_ids,
        )
        if payload.media_asset_ids:
            self.events.append(MessageImageUploaded(message_id=message.id))
        await self.db.commit()
        return self.message_response(message)

    async def messages(self, conversation_id: UUID, user_id: UUID, cursor: str | None, limit: int):
        await self.conversation(conversation_id, user_id)
        values = await self.repo.messages(conversation_id, decode_cursor(cursor), limit)
        page, extra = values[:limit], values[limit:]
        await self.repo.mark_read(conversation_id, user_id)
        await self.db.commit()
        return MessagePage(
            messages=[self.message_response(x) for x in page],
            next_cursor=encode_cursor(page[-1]) if extra and page else None,
        )

    async def message(self, message_id: UUID, user_id: UUID):
        value = await self.repo.get_message(message_id)
        if not value:
            raise MessagingError("Message not found", 404)
        await self.conversation(value.conversation_id, user_id)
        return self.message_response(value)

    async def delete(self, message_id: UUID, user_id: UUID):
        value = await self.repo.get_message(message_id)
        if not value or value.sender_user_id != user_id:
            raise MessagingError("Message not found", 404)
        await self.conversation(value.conversation_id, user_id)
        if not value.deleted_at:
            await self.repo.delete(value)
            await self.db.commit()

    async def attachment(self, message_id: UUID, asset_id: UUID, user_id: UUID):
        value = await self.repo.get_message(message_id)
        if not value:
            raise MessagingError("Message not found", 404)
        await self.conversation(value.conversation_id, user_id)
        asset = await self.repo.asset_for_message(message_id, asset_id)
        if not asset:
            raise MessagingError("Media asset not found", 404)
        return asset
