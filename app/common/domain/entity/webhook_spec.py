from typing import Dict, Any, List, Literal

from pydantic import BaseModel, Field


class WebhookSpec(BaseModel):
    """Webhook 输入规范（运行时工具类，不存储到数据库）

    定义 Graph 如何接收外部输入（HTTP webhook 触发）。

    工作流程：
    1. HTTP Request (JSON/Multipart) → API Router 层
    2. API Router 调用 infer_webhook_spec_from_schema() → WebhookSpec
    3. API Router 根据 webhook_spec 解析请求 → GraphExecuteData
    4. GraphExecutor 转换 GraphExecuteData → ContentBlock → Graph

    支持两种输入类型：
    - application/json: 纯 JSON 请求（无文件上传）
    - multipart/form-data: 表单请求（支持文件上传）
    """

    input_type: Literal["application/json", "multipart/form-data"] = Field(
        default="application/json",
        description="输入类型: 'application/json' 或 'multipart/form-data'"
    )

    input_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="webhook input jsonschema"
    )

    file_fields: List[str] = Field(
        default_factory=list,
        description=(
            "multipart/form-data 中的文件字段名列表\n"
            "例如: ['document', 'image']\n"
            "对应 GraphExecuteData.files 的 keys"
        )
    )

    data_fields: List[str] = Field(
        default_factory=list,
        description=(
            "multipart/form-data 中的数据字段名列表\n"
            "例如: ['title', 'author']\n"
            "对应 GraphExecuteData.json 的 keys"
        )
    )
