from enum import Enum


class AgentCategory(str, Enum):
    """Agent 类型

    - GENERAL: 普通 Agent，执行具体任务
    - ROUTER: 路由 Agent，根据条件决定下一步执行哪个节点
    - ORCHESTRATOR: 编排 Agent，中心化协调所有其他节点
    """
    GENERAL = "general"
    ROUTER = "router"
    ORCHESTRATOR = "orchestrator"
