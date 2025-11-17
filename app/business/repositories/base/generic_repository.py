from typing import Type, Any, Optional, Sequence, cast, List, Tuple

from sqlalchemy import select, desc, asc
from sqlalchemy import update as sql_update, delete, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.business.db.base import T
from app.business.repositories.base.base_repository import BaseRepository


class GenericRepository(BaseRepository[T]):

    def __init__(self, entity_type: Type[T]):

        super().__init__(entity_type)

    @staticmethod
    def parse_sort_string(sort_str: str) -> List[Tuple[str, str]]:
        if not sort_str or not sort_str.strip():
            return []

        sort_fields = []

        for field_spec in sort_str.split(','):
            field_spec = field_spec.strip()
            if not field_spec:
                continue

            if ':' in field_spec:
                field, direction = field_spec.split(':', 1)
                field = field.strip()
                direction = direction.strip().lower()

                if direction not in ('asc', 'desc'):
                    raise ValueError(f"Invalid sort direction '{direction}'. Must be 'asc' or 'desc'")

                sort_fields.append((field, direction))
            else:
                field = field_spec.strip()
                sort_fields.append((field, 'asc'))

        return sort_fields

    def apply_sorting(
            self,
            query: Select[Any],
            entity_type: Type[T],
            sort: Optional[str] = None
    ) -> Select[Any]:
        if not sort:
            return query

        try:
            sort_fields = self.parse_sort_string(sort)
            for field, direction in sort_fields:
                if hasattr(entity_type, field):
                    if direction == 'asc':
                        query = query.order_by(asc(getattr(entity_type, field)))
                    else:
                        query = query.order_by(desc(getattr(entity_type, field)))
                else:
                    raise ValueError(f"Field '{field}' does not exist on {entity_type.__name__}")
            return query
        except ValueError as e:
            raise ValueError(f"Invalid sort parameter: {e}")

    async def _execute_query(
            self,
            session: AsyncSession,
            query,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Sequence[T]:

        if sort:
            query = self.apply_sorting(query, self.entity_type, sort)

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    async def find_by_id(self, session: AsyncSession, id_: Any) -> Optional[T]:

        result = await session.execute(
            select(self.entity_type).filter_by(id=id_)
        )
        return result.scalars().first()

    async def find_all(
            self,
            session: AsyncSession,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None
    ) -> Sequence[T]:
        query = select(self.entity_type)
        return await self._execute_query(session, query, offset, limit, sort)

    async def find_by(
            self,
            session: AsyncSession,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = None,
            **filters
    ) -> Sequence[T]:
        query = select(self.entity_type).filter_by(**filters)
        return await self._execute_query(session, query, offset, limit, sort)

    async def count(self, session: AsyncSession, **filters) -> int:
        query = select(func.count()).select_from(self.entity_type)

        if filters:
            query = query.filter_by(**filters)

        result = await session.execute(query)
        return result.scalar() or 0

    async def save(self, session: AsyncSession, entity: T) -> T:
        session.add(entity)
        await session.flush()
        return entity

    async def save_all(self, session: AsyncSession, entities: list[T]) -> list[T]:
        session.add_all(entities)
        await session.flush()
        return entities

    async def update_by_id(
            self,
            session: AsyncSession,
            entity_id: Any,
            update_data: dict[str, Any]
    ) -> Optional[T]:
        stmt = (
            sql_update(self.entity_type)
            .where(self.entity_type.id == entity_id)  # type: ignore[arg-type]
            .values(**update_data)
            .returning(self.entity_type)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, entity: T) -> T:
        merged = await session.merge(entity)
        await session.flush()
        return merged

    async def delete_by_id(self, session: AsyncSession, entity_id: Any) -> bool:
        stmt = delete(self.entity_type).where(self.entity_type.id == entity_id)  # type: ignore[arg-type]
        result = await session.execute(stmt)
        return cast(int, result.rowcount) > 0
