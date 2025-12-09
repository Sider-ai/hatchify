from typing import Dict, Any, Literal

from pydantic import BaseModel, Field


class InitContext(BaseModel):
    base_url: str
    repo_url: str
    graph_id: str
    graph_input_format: Literal["application/json", "multipart/form-data"] = Field(default="application/json")
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)