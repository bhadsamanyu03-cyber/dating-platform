from alembic import context
from app.core.config import get_settings

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url.unicode_string())


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    engine = create_engine(config.get_main_option("sqlalchemy.url").replace("+asyncpg", "+psycopg"))
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
