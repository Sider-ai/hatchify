from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AgentPatch(BaseModel):
    model: Optional[str] = Field(default=None, description="LLM 模型")
    instruction: Optional[str] = Field(default=None, description="系统指令")
    tools: Optional[List[str]] = Field(default=None, description="工具列表")


class AgentsPatch(BaseModel):
    update: Optional[Dict[str, AgentPatch]] = Field(
        default=None,
        description="更新 Agent，key=name，value=要修改的字段"
    )


class GraphSpecPatchRequest(BaseModel):
    agents: Optional[AgentsPatch] = Field(default=None, description="Agent 节点操作")