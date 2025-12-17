import asyncio

from loguru import logger

from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.graph.tools.math_tool import math_router
from hatchify.core.manager.mcp_manager import mcp_manager
from hatchify.core.manager.predefined_tool_manager import get_pre_defined_tool_configs
from hatchify.core.mcp.mcp_tool_loader import MCPToolLoader

tool_factory = ToolRouter()
pre_defined_tools_config = get_pre_defined_tool_configs()


def load_strands_tools():
    try:
        from strands.tools.loader import load_tools_from_module
        from strands_tools import file_read, image_reader, editor, file_write, shell

        modules = {
            "file_read": file_read,
            "image_reader": image_reader,
            "editor": editor,
            "file_write": file_write,
            "shell": shell,
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


async def async_load_pre_defined_tools():
    """Load predefined tools based on configuration"""
    if pre_defined_tools_config.nano_banana and pre_defined_tools_config.nano_banana.enabled:
        from hatchify.core.graph.tools.nano_banana_tool import nano_banana_router

        tool_factory.include_router(nano_banana_router)
        logger.info("Loaded predefined tool: nano_banana")

    if pre_defined_tools_config.seed_dance and pre_defined_tools_config.seed_dance.enabled:
        from hatchify.core.graph.tools.dou_bao_seed_dance_tool import seed_dance_router

        tool_factory.include_router(seed_dance_router)
        logger.info("Loaded predefined tool: seed_dance")

    if pre_defined_tools_config.seed_dream and pre_defined_tools_config.seed_dream.enabled:
        from hatchify.core.graph.tools.dou_bao_deed_dream_tool import seed_dream_router

        tool_factory.include_router(seed_dream_router)
        logger.info("Loaded predefined tool: seed_dream")

    if pre_defined_tools_config.dou_bao_tts and pre_defined_tools_config.dou_bao_tts.enabled:
        from hatchify.core.graph.tools.dou_bao_tts_tool import dou_bao_tts_router

        tool_factory.include_router(dou_bao_tts_router)
        logger.info("Loaded predefined tool: dou_bao_tts")



tool_factory.include_router(math_router)
