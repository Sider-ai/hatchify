from functools import lru_cache
from typing import Dict, Any

import httpx
from loguru import logger
from pydantic import Field, BaseModel
from strands import tool
from strands.tools.decorator import DecoratedFunctionTool

from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.manager.predefined_tool_manager import get_pre_defined_tool_configs

into_md_router = ToolRouter[DecoratedFunctionTool]()

pre_defined_tool_configs = get_pre_defined_tool_configs()


@lru_cache(maxsize=1)
def lazy_get_into_md_config():
    """Lazy initialize and cache into.md config"""
    config = pre_defined_tool_configs.into_md
    if not (config and config.enabled):
        raise ValueError("into_md: tool is not configured or disabled")
    return config


class IntoMdInputSchema(BaseModel):
    url: str = Field(
        description=(
            "The URL of the webpage to convert to markdown. "
            "Must be a valid HTTP or HTTPS URL."
        ),
        min_length=1,
        max_length=2048
    )


@tool(
    name="into_md",
    description=(
        "Converts any webpage into LLM-friendly markdown format. "
        "Use this tool when you need to read, analyze, or extract content from a webpage. "
        "The tool fetches the webpage and returns clean, structured markdown text "
        "that is optimized for language model processing."
    ),
    inputSchema=IntoMdInputSchema.model_json_schema()
)
async def into_md(url: str) -> Dict[str, Any]:
    """
    Convert a webpage to LLM-friendly markdown using into.md service.

    Args:
        url: The URL of the webpage to convert

    Returns:
        Dict[str, Any]: Response with markdown content

    Raises:
        ValueError: If into_md configuration is invalid
        httpx.HTTPError: If HTTP request fails
    """
    try:
        config = lazy_get_into_md_config()
        into_md_url = f"{config.base_url}/{url}"

        timeout = httpx.Timeout(config.timeout, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(into_md_url)
            response.raise_for_status()

            markdown_content = response.text

        logger.info(f"Successfully converted URL to markdown: {url}")
        return {
            "status": "success",
            "content": [
                {
                    "text": markdown_content
                }
            ]
        }
    except httpx.ConnectError as exc:
        logger.error(f"into_md network connection failed: {exc}")
        raise
    except httpx.HTTPStatusError as exc:
        logger.error(f"into_md request failed with status {exc.response.status_code}: {exc}")
        raise
    except Exception as e:
        logger.error(f"into_md conversion failed: {type(e).__name__}: {e}")
        raise e


into_md_router.register(into_md)
