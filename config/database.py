from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.settings import Settings


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Create a connection pool; connections are opened when first needed."""
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
    )
    return create_async_engine(url, pool_pre_ping=True, echo=False)
