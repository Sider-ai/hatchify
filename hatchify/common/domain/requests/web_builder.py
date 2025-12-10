from pydantic import BaseModel
from strands.types.content import Messages


class WebBuilderConversationRequest(BaseModel):
    graph_id: str
    messages: Messages


class DeployRequest(BaseModel):
    graph_id: str
    redeploy: bool = False