from functools import lru_cache
from typing import Literal, Dict, Any

from loguru import logger
from pydantic import Field, BaseModel
from strands import tool
from strands.tools.decorator import DecoratedFunctionTool

from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.manager.predefined_tool_manager import get_pre_defined_tool_configs

try:
    from volcenginesdkarkruntime import Ark
    from volcenginesdkarkruntime.types.images import ImagesResponse
except ImportError:
    raise ImportError("please install volcengine sdk ark runtime via: uv add 'volcengine-python-sdk[ark]'")

seed_dream_router = ToolRouter[DecoratedFunctionTool]()

pre_defined_tool_configs = get_pre_defined_tool_configs()


@lru_cache(maxsize=1)
def lazy_get_seed_dream_client():
    """Lazy initialize and cache Seed Dream client"""
    config = pre_defined_tool_configs.seed_dream
    if not (config and config.enabled and config.api_key):
        raise ValueError("seed_dream: missing api_key or tool is disabled")
    return Ark(api_key=config.api_key)


@lru_cache(maxsize=1)
def lazy_get_seed_dream_model():
    """Get cached model name"""
    config = pre_defined_tool_configs.seed_dream
    if not (config and config.enabled):
        raise ValueError("seed_dream: tool is not configured")
    return config.model


class SeedDreamInputSchema(BaseModel):
    prompt: str = Field(
        description=(
            "A highly detailed, narrative-driven description of the image to be generated. "
            "Construct a cohesive paragraph that vividly describes the scene, including:\n"
            "1. The main subject with specific textures and micro-details.\n"
            "2. Dynamic composition and action.\n"
            "3. Location and environment.\n"
            "4. Visual style and artistic direction.\n"
            "5. Any text content to render in the image.\n"
            "Add aspect ratio hints like 'Square image' or '16:9' to influence output dimensions."
        ),
        min_length=1,
        max_length=8192
    )
    size: Literal[
        "1K", "2K", "4K",
        "2048x2048", "2304x1728", "1728x2304",
        "2560x1440", "1440x2560", "2496x1664",
        "1664x2496", "3024x1296"
    ] = Field(
        default="2K",
        description="Image dimensions. Use preset sizes (1K/2K/4K) or specific resolutions (e.g., 2048x2048)"
    )


@tool(
    name="seed_dream_generate_image",
    description=(
        "Generates professional-grade images using DouBao's Seed Dream 4.0 model. "
        "Supports composite editing with up to 10 images in one prompt, automatic aspect ratio adaptation, "
        "and 4K ultra-high-definition output. Delivers significant improvements in accuracy and diversity "
        "for Chinese-language generation. Capable of generating up to 15 contextually related images in one sequence. "
        "Use this tool when the user asks to draw, paint, visualize, or generate an image."
    ),
    inputSchema=SeedDreamInputSchema.model_json_schema()
)
async def seed_dream_generate_image(
    prompt: str,
    size: Literal[
        "1K", "2K", "4K",
        "2048x2048", "2304x1728", "1728x2304",
        "2560x1440", "1440x2560", "2496x1664",
        "1664x2496", "3024x1296"
    ] = "2K"
) -> Dict[str, Any]:
    """
    Generate an image from a text prompt using DouBao Seed Dream API.

    Args:
        prompt: Detailed description of the image to generate
        size: Image dimensions (1K/2K/4K or specific resolution)

    Returns:
        Dict[str, Any]

    Raises:
        ValueError: If image generation fails
        Exception: For API errors
    """
    try:
        # Call DouBao API to generate image
        images_response: ImagesResponse = lazy_get_seed_dream_client().images.generate(
            model=lazy_get_seed_dream_model(),
            prompt=prompt,
            size=size,
            sequential_image_generation="disabled",
            response_format="url",
            watermark=False
        )

        if images_response.error:
            logger.error(f"Image generation failed: {images_response.error}")
            raise ValueError(
                f"Failed to generate image. Error: {images_response.error}"
            )

        logger.info(f"Image generated successfully")
        return {
            "status": "success",
            "content": [
                {
                    "text": image.url
                } for image in images_response.data
            ]
        }
    except Exception as e:
        logger.error(f"Image generation failed: {type(e).__name__}: {e}")
        raise e


seed_dream_router.register(seed_dream_generate_image)
