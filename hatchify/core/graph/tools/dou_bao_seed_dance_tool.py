import time
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
    from volcenginesdkarkruntime.types.content_generation.content_generation_task import ContentGenerationTask
    from volcenginesdkarkruntime.types.content_generation.create_task_content_param import CreateTaskContentTextParam, \
        CreateTaskContentImageParam, CreateTaskContentImageDataParam
except ImportError:
    raise ImportError("please install volcengine sdk ark runtime via: uv add 'volcengine-python-sdk[ark]'")

seed_dance_router = ToolRouter[DecoratedFunctionTool]()

pre_defined_tool_configs = get_pre_defined_tool_configs()


@lru_cache(maxsize=1)
def lazy_get_seed_dance_client():
    """Lazy initialize and cache Seed Dance client"""
    config = pre_defined_tool_configs.seed_dance
    if not (config and config.enabled and config.api_key):
        raise ValueError("seed_dance: missing api_key or tool is disabled")
    return Ark(api_key=config.api_key)


@lru_cache(maxsize=1)
def lazy_get_seed_dance_model():
    """Get cached model name"""
    config = pre_defined_tool_configs.seed_dance
    if not (config and config.enabled):
        raise ValueError("seed_dance: tool is not configured")
    return config.model


class SeedDanceInputSchema(BaseModel):
    prompt: str = Field(
        description=(
            "The primary text prompt used to describe video generation content. "
            "The prompt should follow a structured format, clearly describing the subject, actions, scene, "
            "and camera movements in the video in order to generate high-quality content that matches expectations. "
            "Prompt = subject + motion + background + motion + camera + motion"
        ),
        min_length=1,
        max_length=500
    )
    resolution: Literal["420p", "780p", "1080p"] = Field(
        default="1080p",
        description="Video resolution"
    )
    ratio: Literal['16:9', '4:3', '1:1', '3:4', '9:16', '21:9', 'adaptive'] = Field(
        default='16:9',
        description="Video aspect ratio"
    )
    duration: int = Field(
        default=5,
        description="Video duration in seconds",
        ge=2,
        le=12
    )
    frames: int | None = Field(
        default=None,
        description="Supports all integer values in the range [29, 289] that fit the format 25 + 4n, where n is a positive integer",
        ge=29,
        le=289
    )
    frames_per_second: int = Field(
        default=24,
        description="Video frames per second"
    )
    camera_fixed: bool = Field(
        default=False,
        description="Whether the camera is fixed or not"
    )
    first_frame: str | None = Field(
        default=None,
        description="The first frame shown on the screen. Supports URL or base64(data:image/png;base64)"
    )
    last_frame: str | None = Field(
        default=None,
        description="The last frame shown on the screen. Supports URL or base64(data:image/png;base64)"
    )


@tool(
    name="seed_dance_generate_video",
    description=(
        "Generates professional-grade videos using DouBao SeedDance 1.0 Pro model. "
        "Capable of creating 1080P HD videos with smooth motion, rich detail, diverse styles, and cinematic visual quality. "
        "Supports multi-shot storytelling and delivers strong performance in semantic understanding and instruction following. "
        "Use this tool when the user asks to generate, create, or produce a video."
    ),
    inputSchema=SeedDanceInputSchema.model_json_schema()
)
async def seed_dance_generate_video(
    prompt: str,
    resolution: Literal["420p", "780p", "1080p"] = "1080p",
    ratio: Literal['16:9', '4:3', '1:1', '3:4', '9:16', '21:9', 'adaptive'] = '16:9',
    duration: int = 5,
    frames: int | None = None,
    frames_per_second: int = 24,
    camera_fixed: bool = False,
    first_frame: str | None = None,
    last_frame: str | None = None
) -> Dict[str, Any]:
    """
    Generate a video from a text prompt using DouBao SeedDance API.

    Args:
        prompt: Detailed description of the video to generate
        resolution: Video resolution (420p, 780p, 1080p)
        ratio: Video aspect ratio
        duration: Video duration in seconds (2-12)
        frames: Number of frames (29-289, format: 25 + 4n)
        frames_per_second: Video frames per second
        camera_fixed: Whether the camera is fixed
        first_frame: URL or base64 of the first frame
        last_frame: URL or base64 of the last frame

    Returns:
        Dict[str, Any]

    Raises:
        ValueError: If video generation fails
        Exception: For API errors
    """
    try:
        # Build content parameters
        content = []
        prompt_text = prompt

        if resolution:
            prompt_text += f" --resolution {resolution}"
        if ratio:
            prompt_text += f" --ratio {ratio}"
        if duration:
            prompt_text += f" --duration {duration}"
        if frames:
            prompt_text += f" --frames {frames}"
        if frames_per_second:
            prompt_text += f" --framespersecond {frames_per_second}"
        if camera_fixed:
            prompt_text += " --camerafixed true"
        else:
            prompt_text += " --camerafixed false"
        prompt_text += " --watermark true"

        content.append(
            CreateTaskContentTextParam(
                type="text",
                text=prompt_text
            )
        )

        if first_frame:
            content.append(
                CreateTaskContentImageParam(
                    type="image_url",
                    image_url=CreateTaskContentImageDataParam(
                        url=first_frame
                    ),
                    role="first_frame"
                )
            )

        if last_frame:
            content.append(
                CreateTaskContentImageParam(
                    type="image_url",
                    image_url=CreateTaskContentImageDataParam(
                        url=last_frame
                    ),
                    role="last_frame"
                )
            )

        # Call DouBao API to generate video
        create_result = lazy_get_seed_dance_client().content_generation.tasks.create(
            model=lazy_get_seed_dance_model(),
            content=content
        )

        task_id = create_result.id
        logger.info(f"Video generation task created: {task_id}")

        # Poll for task completion
        while True:
            get_result: ContentGenerationTask = lazy_get_seed_dance_client().content_generation.tasks.get(
                task_id=task_id
            )
            status = get_result.status

            if status == "succeeded":
                result_content = get_result.content
                video_url = result_content.video_url

                logger.info(f"Video generated successfully: {task_id}")
                return {
                    "status": "success",
                    "content": [
                        {
                            "text": video_url
                        }
                    ]
                }
            elif status == "failed":
                logger.error(f"Video generation failed: {get_result.error}")
                raise ValueError(
                    f"Failed to generate video. Error: {get_result.error}"
                )
            else:
                logger.info(f"Current status: {status}, retrying after 3 seconds...")
                time.sleep(3)

    except Exception as e:
        logger.error(f"Video generation failed: {type(e).__name__}: {e}")
        raise e


seed_dance_router.register(seed_dance_generate_video)
