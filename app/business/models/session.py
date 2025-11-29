from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    func,
    Enum, )
from sqlalchemy.orm import Mapped, mapped_column

from app.business.db.base import Base
from app.common.domain.enums.session_scene import SessionScene


class SessionTable(Base):
    __tablename__ = "session"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )

    graph_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    # 分支信息：指向父会话和锚点
    parent_session_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    fork_from_message_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    # 用途场景：区分 graph 编辑 / 基于 graph 的网站生成等
    scene: Mapped[SessionScene] = mapped_column(
        Enum(SessionScene),
        nullable=False,
        default=SessionScene.GRAPH_EDIT,
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
