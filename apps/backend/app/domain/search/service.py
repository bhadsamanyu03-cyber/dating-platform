from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.discovery.service import RankingStrategy
from app.domain.search.repository import SearchRepository
from app.domain.search.schemas import ProfileFilters


class SearchService:
    def __init__(self, db: AsyncSession):
        self.repo, self.ranking = SearchRepository(db), RankingStrategy()

    async def users(self, query: str, filters: ProfileFilters, limit: int):
        return [
            self.ranking.profile(value) for value in await self.repo.users(query, filters, limit)
        ]
