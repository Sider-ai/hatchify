from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.models.graph_version import GraphVersionTable
from app.business.repositories.base.generic_repository import GenericRepository
from app.common.domain.enums.graph_version_type import GraphVersionType


class GraphVersionRepository(GenericRepository[GraphVersionTable]):

    def __init__(self):
        super().__init__(GraphVersionTable)

    async def get_max_version_by_graph(
            self,
            session: AsyncSession,
            graph_id: str
    ) -> Optional[int]:
        """获取指定 graph 的最大 version 号"""
        stmt = (
            select(func.max(self.entity_type.version))
            .where(self.entity_type.graph_id == graph_id)  # type: ignore
            .where(self.entity_type.type == GraphVersionType.SNAPSHOT)  # type: ignore
        )
        result = await session.execute(stmt)
        max_version = result.scalar()
        return max_version

    async def get_latest_version_by_graph(
            self,
            session: AsyncSession,
            graph_id: str
    ) -> Optional[GraphVersionTable]:
        """获取指定 graph 的最新版本记录"""
        stmt = (
            select(self.entity_type)
            .where(self.entity_type.graph_id == graph_id)  # type: ignore
            .where(self.entity_type.type == GraphVersionType.SNAPSHOT)  # type: ignore
            .order_by(self.entity_type.version.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_drafts_by_graph(
            self,
            session: AsyncSession,
            graph_id: str,
    ) -> list[GraphVersionTable]:
        """列出指定 graph 的草稿版本（按创建时间升序）"""
        stmt = (
            select(self.entity_type)
            .where(self.entity_type.graph_id == graph_id)  # type: ignore
            .where(self.entity_type.type == GraphVersionType.DRAFT)  # type: ignore
            .order_by(self.entity_type.created_at.asc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
