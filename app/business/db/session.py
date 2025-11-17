from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.common.settings.settings import get_hatchify_settings

settings = get_hatchify_settings()

engine = create_async_engine(url=settings.database.pg_url, pool_pre_ping=True, echo=False)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"{type(e).__name__}: {str(e)}")
            await session.rollback()
            raise


@asynccontextmanager
async def transaction(session: AsyncSession):
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
