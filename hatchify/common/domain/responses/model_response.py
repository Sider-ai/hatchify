from pydantic import BaseModel


class ModelResponse(BaseModel):
    id: str
    name: str
    description: str
