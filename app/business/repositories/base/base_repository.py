import abc
from typing import Type, Sequence, Any, Generic, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.business.db.base import T


class BaseRepository(Generic[T], metaclass=abc.ABCMeta):
    def __init__(self, entity_type: Type[T]):
        self.entity_type = entity_type

    @abc.abstractmethod
    async def find_by_id(self, session: AsyncSession, id_: Any) -> Optional[T]:
        ...

    @abc.abstractmethod
    async def find_all(
            self,
            session: AsyncSession,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Sequence[T]:
        ...

    @abc.abstractmethod
    async def find_by(
            self,
            session: AsyncSession,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None,
            **filters
    ) -> Sequence[T]:
        ...

    @abc.abstractmethod
    async def count(self, session: AsyncSession, **filters) -> int:
        ...

    @abc.abstractmethod
    async def save(self, session: AsyncSession, entity: T) -> T:
        ...

    @abc.abstractmethod
    async def save_all(self, session: AsyncSession, entities: Sequence[T]) -> Sequence[T]:
        ...

    @abc.abstractmethod
    async def update_by_id(self, session: AsyncSession, id_: Any, update_data: dict) -> T:
        ...

    @abc.abstractmethod
    async def update(self, session: AsyncSession, entity: T) -> T:
        ...

    @abc.abstractmethod
    async def delete_by_id(self, session: AsyncSession, id_: Any) -> bool:
        ...
