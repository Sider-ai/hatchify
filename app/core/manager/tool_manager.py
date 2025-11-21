from loguru import logger

from app.core.factory.tool_factory import ToolRouter
from app.core.functions.tools.math_tool import math_router
from app.core.manager.mcp_manager import mcp_manager
from app.core.mcp.mcp_tool_loader import MCPToolLoader

tool_factory = ToolRouter()

tool_factory.include_router(math_router)


def load_mcp_server():
    if enabled_servers := mcp_manager.get_enabled_servers():
        mcp_tools = MCPToolLoader.load_mcp_tools(enabled_servers)
        for tool in mcp_tools:
            tool_factory.register(tool)
            logger.info(tool.tool_name)


async def async_load_mcp_server():
    if enabled_servers := mcp_manager.get_enabled_servers():
        mcp_tools = await MCPToolLoader.async_load_mcp_tools(enabled_servers)
        for tool in mcp_tools:
            tool_factory.register(tool)
            logger.info(tool.tool_name)
