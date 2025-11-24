from typing import List, Optional, Dict, Any, Type

from app.common.domain.enums.agent_category import AgentCategory
from app.utils.json_schema_2_pydantic import jsonschema_to_pydantic
from pydantic import Field, BaseModel, computed_field


class AgentNode(BaseModel):
    """Graph 中的 Agent 节点定义（由 LLM 生成）"""
    name: str = Field(..., description="节点唯一名称")
    model: str = Field(..., description="使用的 LLM 模型")
    instruction: str = Field(..., description="Agent 系统指令")
    category: AgentCategory = Field(
        default=AgentCategory.GENERAL,
        description="Agent 类型: general/router/orchestrator"
    )
    tools: List[str] = Field(
        default_factory=list,
        description="Agent 可用的工具列表"
    )

    # Router/Orchestrator 的输出 Schema (用于文档和验证)
    structured_output_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Agent 输出的 JSON Schema"
    )

    @computed_field
    @property
    def structured_output_model(self) -> Optional[Type[BaseModel]]:
        if not self.structured_output_schema:
            return None
        
        model_name = f"{self.name.capitalize()}Output"
        schema_with_title = {
            "title": model_name,
            **self.structured_output_schema
        }

        return jsonschema_to_pydantic(schema_with_title)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "quality_router",
                "model": "claude-sonnet-4-5-20250929",
                "instruction": "分析内容质量并路由...",
                "category": "router",
                "tools": [],
                "structured_output_schema": {
                    "transport": "object",
                    "properties": {
                        "next_node": {"transport": "string"},
                        "reasoning": {"transport": "string"}
                    },
                    "required": ["next_node"]
                }
            }
        }