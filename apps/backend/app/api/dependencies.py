from collections.abc import AsyncGenerator
from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_database_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(request.app.state.db_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
