from uuid import UUID
from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.matching.models import Match
from app.domain.messaging.models import Conversation, Message
from app.domain.media.models import MediaAsset


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

    async def media(self, asset_id: UUID, owner: UUID):
        return await self.db.scalar(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.owner_user_id == owner,
                MediaAsset.upload_status == "UPLOADED",
            )
        )

    async def add_message(self, message: Message):
        self.db.add(message)
        await self.db.flush()

    async def messages(self, conversation_id: UUID, limit: int):
        return list(
            (
                await self.db.scalars(
                    select(Message)
                    .where(Message.conversation_id == conversation_id, Message.deleted_at.is_(None))
                    .order_by(Message.created_at.desc(), Message.id.desc())
                    .limit(limit)
                )
            ).all()
        )
