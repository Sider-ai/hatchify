from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from hatchify.business.db.base import Base
from hatchify.core.factory.sql_engine_factory import create_sql_engine

engine = create_sql_engine()

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


async def init_db():
    from hatchify.business.models.graph import GraphTable
    from hatchify.business.models.graph_version import GraphVersionTable
    from hatchify.business.models.session import SessionTable
    from hatchify.business.models.messages import MessageTable

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.debug("✅ 数据库表检查完成")
