"""Database base model and engine setup."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings


class Base(DeclarativeBase):
    pass


def get_async_url(url: str) -> str:
    """Convert database URL to async format."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_sync_url(url: str) -> str:
    """Convert database URL to sync format."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


# async engine for API operations
async_url = get_async_url(settings.database_url)
engine = create_async_engine(async_url, echo=settings.log_level == "DEBUG")

# sync engine for SQLAdmin
sync_url = get_sync_url(settings.database_url)
sync_engine = create_engine(sync_url, echo=settings.log_level == "DEBUG")

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
