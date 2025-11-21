from typing import List, Optional, Dict, Any

from pydantic import Field, BaseModel

from app.common.domain.enums.agent_category import AgentCategory


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
        description="Pydantic model 的 JSON Schema（从 model_json_schema() 生成）"
    )

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