from typing import List

from pydantic import BaseModel, Field

from app.common.domain.entity.agent_node_spec import AgentNode
from app.common.domain.entity.processor_node_spec import ProcessorNode


class Edge(BaseModel):
    """Graph 边定义"""
    from_node: str = Field(..., description="起始节点名称")
    to_node: str = Field(..., description="目标节点名称")

    class Config:
        json_schema_extra = {
            "example": {
                "from_node": "agent_1",
                "to_node": "agent_2"
            }
        }


class GraphSpec(BaseModel):
    """完整的 Graph 定义规范"""
    name: str = Field(..., description="Graph 名称")
    description: str = Field(
        default="",
        description="Graph 描述"
    )
    agents: List[AgentNode] = Field(
        default_factory=list,
        description="Agent 节点列表"
    )
    processors: List[ProcessorNode] = Field(
        default_factory=list,
        description="Processor 节点列表（确定性函数节点）"
    )
    nodes: List[str] = Field(
        ...,
        description="所有节点名称列表（agents + processors 的所有节点名）"
    )
    edges: List[Edge] = Field(
        ...,
        description="边列表，定义节点之间的连接关系"
    )
    entry_point: str = Field(
        ...,
        description="入口节点名称（第一个执行的节点）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "idiom_chain",
                "description": "成语接龙 Graph",
                "agents": [
                    {
                        "name": "agent_1",
                        "model": "claude-sonnet-4-5-20250929",
                        "instruction": "开始成语接龙，说出第一个成语",
                        "category": "general",
                        "tools": []
                    },
                    {
                        "name": "agent_2",
                        "model": "claude-sonnet-4-5-20250929",
                        "instruction": "根据上一个成语接龙",
                        "category": "general",
                        "tools": []
                    }
                ],
                "nodes": ["agent_1", "agent_2", "agent_3"],
                "edges": [
                    {"from_node": "agent_1", "to_node": "agent_2"},
                    {"from_node": "agent_2", "to_node": "agent_3"}
                ],
                "entry_point": "agent_1"
            }
        }
