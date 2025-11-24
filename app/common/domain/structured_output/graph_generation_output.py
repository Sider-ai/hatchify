"""GraphSpecGenerator 的 LLM 输出 Models

定义 GraphSpecGenerator 两步生成过程中 LLM 的输出格式：
- Step 1 (Graph 架构): 使用 structured_output 确保类型安全
- Step 2 (Schema 提取): 使用 JSON mode，因为 JSON Schema 是递归结构
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ============================================================
# Step 1: Graph 架构生成的输出
# ============================================================

class AgentArchitecture(BaseModel):
    """Agent 架构定义（Step 1 输出）"""
    name: str = Field(..., description="Agent 唯一名称")
    model: str = Field(..., description="使用的 LLM 模型")
    instruction: str = Field(
        ...,
        description="Agent 的详细指令，必须在自然语言中描述输出格式"
    )
    category: str = Field(
        default="general",
        description="Agent 类型: general, router, orchestrator"
    )
    tools: List[str] = Field(
        default_factory=list,
        description="Agent 可用的工具列表"
    )


class FunctionArchitecture(BaseModel):
    """Function 架构定义（Step 1 输出）"""
    name: str = Field(..., description="Function 实例名称（在 Graph 中的唯一 ID）")
    function_ref: str = Field(..., description="Function 类型（从 function_manager 查找）")


class EdgeArchitecture(BaseModel):
    """边定义（Step 1 输出）"""
    from_node: str = Field(..., description="起始节点名称")
    to_node: str = Field(..., description="目标节点名称")


class GraphArchitectureOutput(BaseModel):
    """Step 1 的完整输出 - Graph 架构"""
    name: str = Field(..., description="Graph 名称")
    description: str = Field(default="", description="Graph 描述")
    agents: List[AgentArchitecture] = Field(
        default_factory=list,
        description="所有 Agent 节点"
    )
    functions: List[FunctionArchitecture] = Field(
        default_factory=list,
        description="所有 Function 节点"
    )
    nodes: List[str] = Field(
        ...,
        description="所有节点名称列表（agents + functions 的所有节点名）"
    )
    edges: List[EdgeArchitecture] = Field(
        ...,
        description="边列表，定义节点之间的连接关系"
    )
    entry_point: str = Field(..., description="入口节点名称")


# ============================================================
# Step 2: Schema 提取的输出
# ============================================================

class AgentSchema(BaseModel):
    """单个 Agent 的 Schema 定义

    注意：structured_output_schema 使用 Dict[str, Any] 是因为 JSON Schema 是递归结构，
    无法用 Pydantic 完全表达。因此这个步骤不适合使用 structured_output。
    """
    agent_name: str = Field(..., description="Agent 名称")
    structured_output_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="Agent 的 JSON Schema（如果不需要结构化输出则为 null）"
    )

    model_config = {
        "extra": "allow"  # 允许额外字段，提高兼容性
    }


class SchemaExtractionOutput(BaseModel):
    """Step 2 的完整输出 - Agent Schemas

    格式（改用列表结构，兼容 Gemini API）：
    {
        "agent_schemas": [
            {
                "agent_name": "agent_1",
                "structured_output_schema": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        ]
    }
    """
    agent_schemas: List[AgentSchema] = Field(
        default_factory=list,
        description="Agent schemas 列表"
    )
