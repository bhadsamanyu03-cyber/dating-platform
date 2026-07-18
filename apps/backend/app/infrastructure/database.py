from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_database_engine(url: str) -> AsyncEngine:
    return create_async_engine(url, pool_pre_ping=True, pool_size=10, max_overflow=20)
