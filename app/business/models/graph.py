from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    func,
    Integer,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.business.db.base import Base


class GraphTable(Base):
    __tablename__ = "graph"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_spec: Mapped[dict] = mapped_column(JSON, nullable=False)  # 当前工作区的 spec（唯一真实源）
    # 指向最新快照版本的 ID
    # NULL = 有未保存的修改
    # NOT NULL = 工作区等于该版本
    current_version_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
