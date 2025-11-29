from typing import Type, List, Optional, Any, Tuple

from fastapi import Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, desc as sql_desc, asc as sql_asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


class CustomParams(Params):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=1000, description="Page size")


class PaginationHelper[T]:
    """分页辅助类"""

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

    @staticmethod
    def apply_sorting(
            query: Select[Any],
            entity_type: Type[T],
            sort: Optional[str] = None
    ) -> Select[Any]:
        if not sort:
            return query

        try:
            sort_fields = PaginationHelper.parse_sort_string(sort)
            for field, direction in sort_fields:
                if hasattr(entity_type, field):
                    if direction == 'asc':
                        query = query.order_by(sql_asc(getattr(entity_type, field)))
                    else:
                        query = query.order_by(sql_desc(getattr(entity_type, field)))
                else:
                    raise ValueError(f"Field '{field}' does not exist on {entity_type.__name__}")
            return query
        except ValueError as e:
            raise ValueError(f"Invalid sort parameter: {e}")

    @staticmethod
    async def paginate_with_sorting(
            session: AsyncSession,
            entity_type: Type[T],
            params: Optional[CustomParams] = None,
            sort: Optional[str] = None,
            **filters
    ) -> Page[T]:
        query = select(entity_type)

        if filters:
            query = query.filter_by(**filters)

        query = PaginationHelper.apply_sorting(query, entity_type, sort)

        return await paginate(session, query, params)
