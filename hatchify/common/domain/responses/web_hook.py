from typing import Literal, Dict, Any, List, Optional

from pydantic import BaseModel, Field


class ExecutionResponse(BaseModel):
    session_id: Optional[str] = Field(default=None)
    execution_id: str


class WebHookInfoResponse(BaseModel):
    graph_id: str
    input_type: Literal["application/json", "multipart/form-data"] = Field(default="application/json")
    data_fields: List[str] = Field(default_factory=list)
    file_fields: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
