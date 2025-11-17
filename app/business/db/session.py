from contextlib import asynccontextmanager
from typing import AsyncIterator

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.infrastructure.settings.settings import get_we0_settings

we0_settings = get_we0_settings()

# 确保使用异步驱动：将 postgresql:// 转换为 postgresql+psycopg://
db_url = we0_settings.pgsql or ""
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_async_engine(
    url=db_url,
    pool_pre_ping=True,
    echo=False,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
)

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


@asynccontextmanager
async def db_transaction():
    """合并的数据库会话和事务上下文管理器，避免嵌套写法"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db_session() -> AsyncSession:
    """创建数据库会话，需要手动调用 commit/rollback/close"""
    return AsyncSessionLocal()


async def commit_db_session(session: AsyncSession) -> None:
    """提交事务并关闭会话"""
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def rollback_db_session(session: AsyncSession) -> None:
    """回滚事务并关闭会话"""
    try:
        await session.rollback()
    finally:
        await session.close()
