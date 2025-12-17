import uuid
from functools import lru_cache
from typing import Literal, Dict, Any

from google import genai
from google.genai import types
from loguru import logger
from pydantic import Field, BaseModel
from strands import tool
from strands.tools.decorator import DecoratedFunctionTool

from hatchify.common.extensions.ext_storage import storage_client
from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.manager.predefined_tool_manager import get_pre_defined_tool_configs

nano_banana_router = ToolRouter[DecoratedFunctionTool]()

pre_defined_tool_configs = get_pre_defined_tool_configs()


@lru_cache(maxsize=1)
def lazy_get_gemini_client():
    """Lazy initialize and cache Gemini client"""
    config = pre_defined_tool_configs.nano_banana
    if not (config and config.enabled and config.api_key):
        raise ValueError("nano_banana: missing api_key or tool is disabled")
    return genai.Client(api_key=config.api_key)


@lru_cache(maxsize=1)
def lazy_get_gemini_model():
    """Get cached model name"""
    config = pre_defined_tool_configs.nano_banana
    if not (config and config.enabled):
        raise ValueError("nano_banana: tool is not configured")
    return config.model


class NanoBananaInputSchema(BaseModel):
    prompt: str = Field(
        description=(
            "A highly detailed, narrative-driven English description of the image to be generated. "
            "DO NOT use list formats (like 'Subject:..., Style:...'). "
            "Instead, construct a cohesive paragraph that vividly describes the scene, including:\n"
            "1. The main subject with specific textures and micro-details.\n"
            "2. Dynamic lighting (e.g., volumetric fog, cinematic rim lighting, golden hour).\n"
            "3. Camera composition (e.g., low angle, wide lens, shallow depth of field).\n"
            "4. Atmosphere and mood (e.g., dystopian, ethereal, vibrant).\n"
            "5. Technical keywords for style (e.g., 'Unreal Engine 5 render', '8k resolution', 'Shot on 35mm film')."
        ),
        min_length=1,
        max_length=8192
    )
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"] = Field(
        default="16:9",
        description="Detailed aspect ratio of the image"
    )
    image_size: Literal["1K", "2K", "4K"] = Field(
        default="1K",
        description="Resolution scale of the image."
    )


@tool(
    name="gemini_generate_image",
    description=(
            "Generates professional-grade images using Google's state-of-the-art Imagen 3 model. "
            "Capable of creating photorealistic photography, complex digital art, 3D renders, and stylistic illustrations. "
            "Use this tool when the user asks to draw, paint, visualize, or generate an image."
    ),
    inputSchema=NanoBananaInputSchema.model_json_schema()
)
async def gemini_generate_image(
        prompt: str,
        aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"] = "16:9",
        image_size: Literal["1K", "2K", "4K"] = "1K"
) -> Dict[str, Any]:
    """
    Generate an image from a text prompt using Gemini API.

    Args:
        prompt: Detailed description of the image to generate
        aspect_ratio: Detailed aspect ratio of the image
        image_size: Detailed aspect ratio of the image

    Returns:
        Dict[str, Any]

    Raises:
        ValueError: If image generation fails or no image data received
        Exception: For API errors or storage failures
    """

    try:

        # Call Gemini API to generate image
        response = await lazy_get_gemini_client().aio.models.generate_content(
            model=lazy_get_gemini_model(),
            contents=[f"Generate a high-quality, detailed image of: {prompt}"],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size
                ),
            )
        )

        # Extract image data from response
        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]

        if not image_parts:
            logger.error(f"No image data received for prompt: {prompt}")
            raise ValueError(
                f"Failed to generate image. The API returned no image data. "
                f"Please try rephrasing your prompt."
            )

        # Store image in cloud storage
        storage_key = f"images/{uuid.uuid4()}.png"
        await storage_client.save(
            key=storage_key,
            data=image_parts[0],
            mimetype="image/png",
        )

        # Generate pre-signed URL (valid for 7 days)
        url = await storage_client.get_pre_signed_url(
            key=storage_key,
            expires_in=3600 * 24 * 7,
        )

        logger.info(f"Image generated successfully: {storage_key}")
        return {
            "status": "success",
            "content": [
                {
                    "text": url
                }
            ]
        }
    except Exception as e:
        logger.error(f"Image generation failed: {type(e).__name__}: {e}")
        raise e


nano_banana_router.register(gemini_generate_image)
