from __future__ import annotations

import re
from typing import Any, Callable, Dict

from mcp import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from app.common.domain.entity.mcp_card import MCPServerCard, ToolFilterConfig


class MCPTransportFactory:
    @staticmethod
    def create_transport_factory(
            server: MCPServerCard,
    ) -> Callable:
        match server.transport:
            case "stdio":
                return MCPTransportFactory._create_stdio_factory(server)
            case "sse":
                return MCPTransportFactory._create_sse_factory(server)
            case "streamablehttp":
                return MCPTransportFactory._create_streamablehttp_factory(server)
            case _:
                raise ValueError(f"Unsupported transport type: {server.transport}")

    @staticmethod
    def _create_stdio_factory(server: MCPServerCard) -> Callable:
        """创建 stdio transport factory"""
        params = StdioServerParameters(
            command=server.command
        )
        if server.args:
            params.args = server.args
        if server.env:
            params.env = server.env
        if server.cwd:
            params.cwd = server.cwd
        if server.encoding:
            params.encoding = server.encoding
        if server.encoding_error_handler:
            params.encoding_error_handler = server.encoding_error_handler
        return lambda: stdio_client(params)

    @staticmethod
    def _create_sse_factory(server: MCPServerCard) -> Callable:
        client_kwargs: Dict[str, Any] = {}
        if server.headers:
            client_kwargs["headers"] = server.headers
        if server.timeout:
            client_kwargs["timeout"] = server.timeout
        if server.sse_read_timeout:
            client_kwargs["sse_read_timeout"] = server.sse_read_timeout
        return lambda: sse_client(
            url=server.url,
            **client_kwargs,
        )

    @staticmethod
    def _create_streamablehttp_factory(server: MCPServerCard) -> Callable:
        client_kwargs: Dict[str, Any] = {}
        if server.headers:
            client_kwargs["headers"] = server.headers
        if server.timeout:
            client_kwargs["timeout"] = server.timeout
        if server.sse_read_timeout:
            client_kwargs["sse_read_timeout"] = server.sse_read_timeout
        if server.terminate_on_close:
            client_kwargs["terminate_on_close"] = server.terminate_on_close
        return lambda: streamablehttp_client(
            url=server.url,
            **client_kwargs,
        )

    @staticmethod
    def create_tool_filters(
            tool_filter_config: ToolFilterConfig | None,
    ) -> dict[str, list] | None:
        """将 ToolFilterConfig 转换为 strands MCPClient 所需的格式

        Args:
            tool_filter_config: 工具过滤配置

        Returns:
            符合 MCPClient 的 tool_filters 格式
        """
        if not tool_filter_config:
            return None

        result: dict[str, list] = {}

        # 处理 allowed 列表
        if tool_filter_config.allowed:
            result["allowed"] = MCPTransportFactory._process_filter_list(
                tool_filter_config.allowed
            )

        # 处理 rejected 列表
        if tool_filter_config.rejected:
            result["rejected"] = MCPTransportFactory._process_filter_list(
                tool_filter_config.rejected
            )

        return result if result else None

    @staticmethod
    def _process_filter_list(filters: list[str]) -> list[str | Any]:
        """处理过滤器列表,将 regex: 开头的转换为 re.Pattern

        Args:
            filters: 过滤器字符串列表

        Returns:
            处理后的列表,包含字符串和正则表达式对象
        """
        processed = []
        for item in filters:
            if item.startswith("regex:"):
                # 去掉 "regex:" 前缀并编译为正则表达式
                pattern = item[6:]  # 去掉 "regex:"
                processed.append(re.compile(pattern))
            else:
                processed.append(item)
        return processed
