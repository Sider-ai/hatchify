from pydantic import BaseModel
from strands.types.content import Messages


class WebBuilderConversationRequest(BaseModel):
    graph_id:str
    messages: Messages