from typing import Optional

from pydantic import Field

from app.common.domain.enums.session_scene import SessionScene
from app.common.domain.requests.base import BasePageRequest


class PageSessionRequest(BasePageRequest):
    graph_id: Optional[str] = Field(default=None, description="按 graph_id 过滤")
    scene: Optional[SessionScene] = Field(default=None, description="按 scene 过滤")
