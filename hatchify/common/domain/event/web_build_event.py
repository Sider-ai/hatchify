from typing import Optional, Dict, Any, List, Literal, Union, TypeAlias

from pydantic import BaseModel, Field
from strands.types.tools import ToolResultStatus

from hatchify.common.domain.event.base_event import PingEvent, DoneEvent, StartEvent, CancelEvent, ErrorEvent
from hatchify.common.domain.event.execute_event import ResultEvent


class DeltaEvent(BaseModel):
    content: Optional[Union[str, Dict[str, Any], List[Union[str, Dict[str, Any]]]]]
    type: Literal["delta"] = Field(default="delta", exclude=True)


class ToolCallItem(BaseModel):
    tool_call_id: str
    tool_name: str
    args: Optional[Dict[str, Any]] = None


class ToolCallEvent(BaseModel):
    tool_calls: List[ToolCallItem]
    type: Literal["tool_call"] = Field(default="tool_call", exclude=True)


class ToolOutputEvent(BaseModel):
    tool_call_id: str
    content: Optional[Union[str, List[Union[str, Dict]]]] = Field(default=None)
    status: ToolResultStatus

    type: Literal["tool_result"] = Field(default="tool_output", exclude=True)


WebBuildEventData: TypeAlias = Union[
    StartEvent,
    PingEvent,
    CancelEvent,
    ErrorEvent,
    ResultEvent,
    DoneEvent,
    DeltaEvent,
    ToolCallEvent,
    ToolOutputEvent
]
WebBuildEventType = Literal[
    "start",
    "ping",
    "cancel",
    "error",
    "result",
    "done",
    "delta",
    "tool_call",
    "tool_output"
]
