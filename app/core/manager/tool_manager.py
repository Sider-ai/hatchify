import asyncio

from loguru import logger

from app.core.factory.tool_factory import ToolRouter
from app.core.manager.mcp_manager import mcp_manager
from app.core.mcp.mcp_tool_loader import MCPToolLoader
from app.core.tools.math_tool import math_router

tool_factory = ToolRouter()

tool_factory.include_router(math_router)


def load_strands_tools():
    try:
        from strands.tools.loader import load_tools_from_module
        from strands_tools import file_read, image_reader, editor, file_write, diagram

        modules = {
            "file_read": file_read,
            "image_reader": image_reader,
            "editor": editor,
            "file_write": file_write,
            "diagram": diagram
        }

        for module_name, module in modules.items():
            tools = load_tools_from_module(module, module_name)
            for tool in tools:
                tool_factory.register(tool)
                logger.info(f"Loaded strands_tool: {tool.tool_name}")
    except ImportError as e:
        logger.warning(f"Failed to load strands_tools: {e}")


async def async_load_strands_tools():
    await asyncio.to_thread(load_strands_tools)


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
