from typing import Type, Collection, Any, Optional

from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.db.base import T
from app.business.manager.repository_manager import RepositoryManager
from app.business.repositories.base.base_repository import BaseRepository
from app.business.services.base.base_service import BaseService
from app.business.utils.pagination_utils import CustomParams


class GenericService(BaseService[T]):
    def __init__(
            self,
            entity_type: Type[T],
            repository_class: Type[BaseRepository[T]]
    ):
        super().__init__(entity_type)
        self._repository: BaseRepository[T] = RepositoryManager.get_repository(repository_class)

    @property
    def repository(self) -> BaseRepository[T]:
        return self._repository

    async def get_by_id(
            self,
            session: AsyncSession,
            entity_id: Any
    ) -> Optional[T]:
        return await self._repository.find_by_id(session, entity_id)

    async def get_all(
            self,
            session: AsyncSession,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Collection[T]:
        return await self._repository.find_all(session, offset, limit, sort)

    async def get_list(
            self,
            session: AsyncSession,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None,
            **filters
    ) -> Collection[T]:
        return await self._repository.find_by(
            session, offset, limit, sort, **filters
        )

    async def count(
            self,
            session: AsyncSession,
            **filters
    ) -> int:
        return await self._repository.count(session, **filters)

    async def create(
            self,
            session: AsyncSession,
            entity_data: dict,
            commit: bool = True
    ) -> T:
        try:
            entity = self.entity_type(**entity_data)
            result = await self._repository.save(session, entity)

            if commit:
                await session.commit()
                await session.refresh(result)

            return result
        except Exception as e:
            if commit:
                await session.rollback()
            raise

    async def batch_create(
            self,
            session: AsyncSession,
            entities_data: list[dict],
            commit: bool = True
    ) -> Collection[T]:
        try:
            entities = [self.entity_type(**data) for data in entities_data]
            results = await self._repository.save_all(session, entities)

            if commit:
                await session.commit()
                for entity in results:
                    await session.refresh(entity)

            return results
        except Exception as e:
            if commit:
                await session.rollback()
            raise

    async def update_by_id(
            self,
            session: AsyncSession,
            entity_id: Any,
            update_data: dict,
            commit: bool = True
    ) -> Optional[T]:
        try:
            entity = await self._repository.find_by_id(session, entity_id)
            if not entity:
                raise Exception(
                    f"{self.entity_type.__name__} with id {entity_id} not found"
                )

            result = await self._repository.update_by_id(session, entity_id, update_data)

            if commit:
                await session.commit()
                await session.refresh(result)

            return result
        except Exception as e:
            if commit:
                await session.rollback()
            raise

    async def delete_by_id(
            self,
            session: AsyncSession,
            entity_id: Any,
            commit: bool = True
    ) -> bool:
        try:
            result = await self._repository.delete_by_id(session, entity_id)

            if result and commit:
                await session.commit()

            return result
        except Exception as e:
            if commit:
                await session.rollback()
            raise

    async def get_paginated(
            self,
            session: AsyncSession,
            params: Optional[CustomParams] = None,
            sort: Optional[str] = None
    ) -> Page[T]:
        return await self._repository.paginate(session, params, sort)

    async def get_paginated_list(
            self,
            session: AsyncSession,
            params: Optional[CustomParams] = None,
            sort: Optional[str] = None,
            **filters
    ) -> Page[T]:
        return await self._repository.paginate_by(session, params, sort, **filters)
