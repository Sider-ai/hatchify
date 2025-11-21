from __future__ import annotations

from typing import Any, Dict

from strands.tools.mcp import MCPClient
from strands.tools.mcp.mcp_types import MCPToolResult
from strands.types._events import ToolResultEvent
from strands.types.tools import AgentTool, ToolContext, ToolSpec, ToolUse, ToolGenerator

from app.common.domain.entity.mcp_card import MCPServerCard
from app.core.factory.mcp_transport_factory import MCPTransportFactory


class MCPToolWrapper(AgentTool):

    def __init__(
            self,
            server_config: MCPServerCard,
            tool_name: str,
            tool_spec: ToolSpec
    ):
        super().__init__()
        self._server_config = server_config
        self._tool_name = tool_name
        self._tool_spec = tool_spec

        self._transport_factory = MCPTransportFactory.create_transport_factory(
            server_config
        )
        self.mark_dynamic()

    @property
    def tool_name(self) -> str:
        return self._tool_name

    @property
    def tool_spec(self) -> ToolSpec:
        return self._tool_spec

    @property
    def tool_type(self) -> str:
        return "function"

    async def stream(self, tool_use: ToolUse, invocation_state: dict[str, Any], **kwargs: Any) -> ToolGenerator:
        mcp_client = MCPClient(self._transport_factory)
        result = await mcp_client.call_tool_async(
            tool_use_id=tool_use["toolUseId"],
            name=self._tool_name,
            arguments=tool_use["input"],
        )
        yield ToolResultEvent(result)

    def __call__(
            self,
            tool_use_id: str,
            arguments: Dict[str, Any],
            tool_context: ToolContext | None = None,
    ) -> MCPToolResult:
        mcp_client = MCPClient(self._transport_factory)
        with mcp_client:
            result = mcp_client.call_tool_sync(
                tool_use_id=tool_use_id,
                name=self._tool_name,
                arguments=arguments,
            )
            return result
