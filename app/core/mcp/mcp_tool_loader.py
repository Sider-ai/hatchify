from __future__ import annotations

import asyncio
from typing import List, Any, Dict

from loguru import logger
from strands.tools.mcp import MCPClient

from app.common.domain.entity.mcp_card import MCPServerCard
from app.core.factory.mcp_transport_factory import MCPTransportFactory
from app.core.mcp.mcp_tool_wrapper import MCPToolWrapper


class MCPToolLoader:

    @staticmethod
    def load_tools_from_server(
            server: MCPServerCard,
    ) -> List[MCPToolWrapper]:

        transport_factory = MCPTransportFactory.create_transport_factory(server)
        tool_filters = MCPTransportFactory.create_tool_filters(server.tool_filters)

        mcp_client_kwargs: Dict[str, Any] = {}
        if server.prefix:
            mcp_client_kwargs["prefix"] = server.prefix
        if tool_filters:
            mcp_client_kwargs["tool_filters"] = tool_filters
        if server.startup_timeout:
            mcp_client_kwargs["startup_timeout"] = server.startup_timeout

        mcp_client = MCPClient(
            transport_factory,
            **mcp_client_kwargs
        )

        wrappers = []

        with mcp_client:
            tools = mcp_client.list_tools_sync()
            for tool in tools:
                tool_name = tool.tool_name
                tool_spec = tool.tool_spec

                wrapper = MCPToolWrapper(
                    server_config=server,
                    tool_name=tool_name,
                    tool_spec=tool_spec
                )
                wrappers.append(wrapper)

        return wrappers

    @staticmethod
    def load_mcp_tools(
            servers: List[MCPServerCard],
    ) -> List[MCPToolWrapper]:
        all_wrappers = []

        for server in servers:
            try:
                wrappers = MCPToolLoader.load_tools_from_server(server)
                all_wrappers.extend(wrappers)
            except Exception as e:
                logger.exception(f"✗ Failed to load tools from '{server.name}': {e}")

        return all_wrappers

    @staticmethod
    async def async_load_mcp_tools(
            servers: List[MCPServerCard],
    ) -> List[MCPToolWrapper]:
        all_wrappers = []
        tasks = [
            asyncio.create_task(
                asyncio.to_thread(
                    MCPToolLoader.load_tools_from_server, server
                )
            )
            for server in servers
        ]
        for task in asyncio.as_completed(tasks):
            all_wrappers.extend(await task)
        return all_wrappers
