from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def async_database_url(url: str) -> URL:
    parsed = make_url(url)
    if parsed.drivername.endswith("+asyncpg"):
        return parsed
    return parsed.set(drivername="postgresql+asyncpg")


def sync_database_url(url: str) -> URL:
    parsed = make_url(url)
    if parsed.drivername.endswith("+psycopg"):
        return parsed
    if parsed.drivername in {"postgresql", "postgresql+psycopg2", "postgresql+asyncpg"}:
        return parsed.set(drivername="postgresql+psycopg")
    return parsed


def create_database_engine(url: str) -> AsyncEngine:
    return create_async_engine(
        async_database_url(url),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
