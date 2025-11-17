from typing import Protocol, Any, runtime_checkable, TypeVar

from sqlalchemy.orm import DeclarativeBase


@runtime_checkable
class HasId(Protocol):
    id: Any


class Base(DeclarativeBase):
    pass


T = TypeVar('T', bound=HasId)
