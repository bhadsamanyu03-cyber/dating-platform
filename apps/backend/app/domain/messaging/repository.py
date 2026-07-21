from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.matching.models import Match
from app.domain.media.models import MediaAsset
from app.domain.messaging.models import Conversation, Message, MessageMedia


class MessagingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_conversation(self, match_id: UUID) -> Conversation:
        result = await self.db.execute(
            insert(Conversation)
            .values(match_id=match_id)
            .on_conflict_do_nothing(index_elements=["match_id"])
            .returning(Conversation)
        )
        return result.scalar_one_or_none() or await self.db.scalar(
            select(Conversation).where(Conversation.match_id == match_id)
        )

    async def conversation_for_user(self, conversation_id: UUID, user_id: UUID):
        return await self.db.scalar(
            select(Conversation)
            .join(Match, Match.id == Conversation.match_id)
            .where(
                Conversation.id == conversation_id,
                or_(Match.user_one_id == user_id, Match.user_two_id == user_id),
            )
        )

    async def list_for_user(self, user_id: UUID, limit: int):
        return list(
            (
                await self.db.scalars(
                    select(Conversation)
                    .join(Match)
                    .where(or_(Match.user_one_id == user_id, Match.user_two_id == user_id))
                    .order_by(Conversation.updated_at.desc())
                    .limit(limit)
                )
            ).all()
        )

    async def media(self, asset_ids: list[UUID], owner: UUID):
        if not asset_ids:
            return []
        assets = list(
            (
                await self.db.scalars(
                    select(MediaAsset).where(
                        MediaAsset.id.in_(asset_ids),
                        MediaAsset.owner_user_id == owner,
                        MediaAsset.upload_status == "UPLOADED",
                        MediaAsset.media_type == "IMAGE",
                    )
                )
            ).all()
        )
        return assets

    async def existing_message(self, sender_id: UUID, client_message_id: UUID):
        return await self.db.scalar(
            select(Message)
            .options(selectinload(Message.media))
            .where(
                Message.sender_user_id == sender_id, Message.client_message_id == client_message_id
            )
        )

    async def add_message(self, message: Message, asset_ids: list[UUID]):
        self.db.add(message)
        await self.db.flush()
        for ordering, asset_id in enumerate(asset_ids):
            self.db.add(
                MessageMedia(message_id=message.id, media_asset_id=asset_id, ordering=ordering)
            )
        await self.db.flush()
        return await self.get_message(message.id)

    async def get_message(self, message_id: UUID):
        return await self.db.scalar(
            select(Message).options(selectinload(Message.media)).where(Message.id == message_id)
        )

    async def messages(
        self, conversation_id: UUID, cursor: tuple[datetime, UUID] | None, limit: int
    ):
        query = (
            select(Message)
            .options(selectinload(Message.media))
            .where(Message.conversation_id == conversation_id)
        )
        if cursor:
            created_at, message_id = cursor
            query = query.where(
                or_(
                    Message.created_at < created_at,
                    and_(Message.created_at == created_at, Message.id < message_id),
                )
            )
        return list(
            (
                await self.db.scalars(
                    query.order_by(Message.created_at.desc(), Message.id.desc()).limit(limit + 1)
                )
            ).all()
        )

    async def delete(self, message: Message):
        message.deleted_at = datetime.now().astimezone()
        message.text_content = "This message was deleted."
        await self.db.flush()

    async def mark_read(self, conversation_id: UUID, reader_id: UUID):
        now = datetime.now().astimezone()
        await self.db.execute(
            update(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.sender_user_id != reader_id,
                Message.deleted_at.is_(None),
                Message.read_at.is_(None),
            )
            .values(read_at=now, delivered_at=now)
        )

    async def asset_for_message(self, message_id: UUID, asset_id: UUID):
        return await self.db.scalar(
            select(MediaAsset)
            .join(MessageMedia)
            .where(MessageMedia.message_id == message_id, MessageMedia.media_asset_id == asset_id)
        )
