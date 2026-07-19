from datetime import date
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.identity.models import User
from app.domain.profile.models import UserProfile
from app.domain.search.schemas import ProfileFilters


class SearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def users(self, query: str, filters: ProfileFilters, limit: int):
        value = f"%{query.strip()}%"
        q = (
            select(UserProfile)
            .join(User)
            .where(
                User.is_active.is_(True),
                User.deleted_at.is_(None),
                or_(UserProfile.username.ilike(value), UserProfile.display_name.ilike(value)),
            )
        )
        if filters.gender:
            q = q.where(UserProfile.gender == filters.gender)
        if filters.profile_complete_only:
            q = q.where(UserProfile.profile_completion_percentage >= 100)
        if filters.age_min is not None:
            q = q.where(
                UserProfile.date_of_birth
                <= date.today().replace(year=date.today().year - filters.age_min)
            )
        if filters.age_max is not None:
            q = q.where(
                UserProfile.date_of_birth
                >= date.today().replace(year=date.today().year - filters.age_max - 1)
            )
        return list((await self.db.scalars(q.order_by(UserProfile.username).limit(limit))).all())
