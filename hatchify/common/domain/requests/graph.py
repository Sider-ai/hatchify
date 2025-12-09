from typing import Optional

from pydantic import BaseModel, Field
from strands.types.content import Messages

from hatchify.common.domain.enums.conversation_mode import ConversationMode
from hatchify.common.domain.requests.base import BasePageRequest


class PageGraphRequest(BasePageRequest):
    ...


class UpdateGraphRequest(BaseModel):
    """
    更新 Graph 请求
    - 如果更新了 spec，current_version_id 会设为 NULL（标记有未保存修改）
    - 如果只更新 name/description，current_version_id 不变
    """
    name: Optional[str] = Field(default=None, description="图的名称")
    description: Optional[str] = Field(default=None, description="图的描述")
    spec: Optional[dict] = Field(default=None, description="图的 spec")


class GraphConversationRequest(BaseModel):
    messages: Messages
    mode: ConversationMode = Field(
        default=ConversationMode.EDIT,
        description="对话模式：chat（不修改）或 edit（生成并覆盖 spec）"
    )
