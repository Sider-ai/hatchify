from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = Field(default=None)
