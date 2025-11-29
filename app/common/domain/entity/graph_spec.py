from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.common.domain.entity.agent_node_spec import AgentNode
from app.common.domain.entity.function_node_spec import FunctionNode


class ConditionRule(BaseModel):
    """单条条件规则定义"""
    field: str = Field(..., description="要检查的字段名（来自上游节点 structured_output）")
    op: str = Field(
        ...,
        description=(
            "比较运算符，支持 ==, !=, >, >=, <, <=, in, not_in, contains, not_contains, "
            "regex, regex_not, startswith, endswith, between, is_true, is_false, exists, not_exists"
        ),
    )
    value: Any = Field(..., description="用于比较的目标值（部分运算符可忽略此值）")


class Edge(BaseModel):
    """Graph 边定义"""
    from_node: str = Field(..., description="起始节点名称")
    to_node: str = Field(..., description="目标节点名称")
    logic: Optional[str] = Field(
        default=None,
        description="规则组合逻辑：'and' 或 'or'，不填默认 and"
    )
    rules: Optional[List[ConditionRule]] = Field(
        default=None,
        description="可选的条件规则列表，用于决定是否穿越该边"
    )
    json_logic: Optional[Dict[str, Any]] = Field(
        default=None,
        description="可选的 JSONLogic 表达式，优先于 rules。参考 https://jsonlogic.com/ 规范"
    )


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
    functions: List[FunctionNode] = Field(
        default_factory=list,
        description="Function 节点列表（确定性函数节点）"
    )
    nodes: List[str] = Field(
        ...,
        description="所有节点名称列表（agents + functions 的所有节点名）"
    )
    edges: List[Edge] = Field(
        ...,
        description="边列表，定义节点之间的连接关系"
    )
    entry_point: str = Field(
        ...,
        description="入口节点名称（第一个执行的节点）"
    )
    input_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Graph 输入 JSON Schema（用于前端表单生成和输入验证）\n"
            "- 文件字段应标记为 format: 'binary'\n"
            "- Webhook 处理方式（JSON vs Multipart）会根据 schema 自动推断\n"
            "- 如果存在 format: 'binary' 字段 → 使用 multipart/form-data\n"
            "- 否则 → 使用 application/json"
        )
    )
    output_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="由终端节点解析"
    )
