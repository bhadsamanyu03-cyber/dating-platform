from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def async_database_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.drivername.endswith("+asyncpg"):
        return str(parsed)
    return str(parsed.set(drivername="postgresql+asyncpg"))


def sync_database_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.drivername.endswith("+psycopg"):
        return str(parsed)
    if parsed.drivername in {"postgresql", "postgresql+psycopg2", "postgresql+asyncpg"}:
        return str(parsed.set(drivername="postgresql+psycopg"))
    return str(parsed)


def create_database_engine(url: str) -> AsyncEngine:
    return create_async_engine(async_database_url(url), pool_pre_ping=True, pool_size=10, max_overflow=20)
