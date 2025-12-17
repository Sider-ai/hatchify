import base64
import json
import uuid
from functools import lru_cache
from typing import Dict, Any

import httpx
from loguru import logger
from pydantic import Field, BaseModel
from strands import tool
from strands.tools.decorator import DecoratedFunctionTool

from hatchify.common.extensions.ext_storage import storage_client
from hatchify.core.factory.tool_factory import ToolRouter
from hatchify.core.manager.predefined_tool_manager import get_pre_defined_tool_configs

dou_bao_tts_router = ToolRouter[DecoratedFunctionTool]()

pre_defined_tool_configs = get_pre_defined_tool_configs()


@lru_cache(maxsize=1)
def lazy_get_dou_bao_tts_config():
    """Lazy initialize and cache DouBao TTS config"""
    config = pre_defined_tool_configs.dou_bao_tts
    if not (config and config.enabled):
        raise ValueError("dou_bao_tts: tool is not configured or disabled")
    if not config.resource_id:
        raise ValueError("dou_bao_tts: missing resource_id")
    if not config.speaker:
        raise ValueError("dou_bao_tts: missing speaker")
    if not config.api_key:
        raise ValueError("dou_bao_tts: missing api_key")

    return config


async def _stream_dou_bao_tts_audio(text: str) -> bytes:
    """
    Stream audio data from DouBao TTS API.

    Args:
        text: Text to synthesize into speech

    Returns:
        bytes: Audio data in MP3 format

    Raises:
        RuntimeError: If TTS API returns an error or no audio data
        httpx.HTTPError: If HTTP request fails
    """
    tts_config = lazy_get_dou_bao_tts_config()

    headers = {
        "x-api-key": tts_config.api_key,
        "X-Api-Resource-Id": tts_config.resource_id,
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }

    payload = {
        "req_params": {
            "text": text,
            "speaker": tts_config.speaker,
            "additions": json.dumps({
                "enable_language_detector": True,  # 自动识别语种
                "disable_markdown_filter": True,  # 是否开启markdown解析过滤
                "disable_emoji_filter": False,  # 是否开启emoji解析过滤
                "enable_latex_tn": True,  # 是否可以播报latex公式
                "disable_default_bit_rate": True,  # 禁用默认bit rate
                "max_length_to_filter_parenthesis": 0,  # 是否过滤括号内的部分
                "cache_config": {
                    "text_type": 1,
                    "use_cache": True,
                },
            }, ensure_ascii=False),
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000,
            },
        },
    }

    audio_buffer = bytearray()
    transport = httpx.AsyncHTTPTransport(retries=3)
    timeout = httpx.Timeout(60.0, connect=30.0)

    try:
        async with httpx.AsyncClient(transport=transport, timeout=timeout) as client:
            async with client.stream(
                "POST",
                tts_config.url,
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode DouBao TTS chunk: {line}")
                        continue

                    code = chunk.get("code", 0)

                    if code == 0 and chunk.get("data"):
                        audio_buffer.extend(base64.b64decode(chunk["data"]))
                        continue

                    if code == 0 and chunk.get("sentence"):
                        logger.debug("DouBao TTS sentence metadata received.")
                        continue

                    if code == 20000000:
                        break

                    if code != 0:
                        message = chunk.get("message") or chunk
                        raise RuntimeError(f"DouBao TTS error {code}: {message}")
    except httpx.ConnectError as exc:
        logger.error(f"DouBao TTS network connection failed: {exc}")
        raise
    except httpx.HTTPError as exc:
        logger.error(f"DouBao TTS request failed: {exc}")
        raise

    if not audio_buffer:
        raise RuntimeError("DouBao TTS returned no audio data.")

    return bytes(audio_buffer)


class DouBaoTTSInputSchema(BaseModel):
    text: str = Field(
        description="Text to synthesize into speech. Supports Chinese and English with automatic language detection.",
        min_length=1,
        max_length=10000
    )


@tool(
    name="dou_bao_text_to_speech",
    description=(
        "Converts text to speech using DouBao TTS (Text-to-Speech) service. "
        "Generates high-quality speech audio with natural voice and emotion. "
        "Supports automatic language detection for Chinese and English, "
        "with markdown and LaTeX formula parsing capabilities. "
        "Returns a pre-signed URL to download the generated MP3 audio file. "
        "Use this tool when the user asks to convert text to audio, read text aloud, or generate speech."
    ),
    inputSchema=DouBaoTTSInputSchema.model_json_schema()
)
async def dou_bao_text_to_speech(text: str) -> Dict[str, Any]:
    """
    Generate speech audio from text using DouBao TTS API.

    Args:
        text: Text to synthesize into speech

    Returns:
        Dict[str, Any]: Response with pre-signed URL to the audio file

    Raises:
        ValueError: If TTS configuration is invalid
        RuntimeError: If TTS API returns an error
        Exception: For other API or storage errors
    """
    try:
        # Generate audio via DouBao TTS
        audio_bytes = await _stream_dou_bao_tts_audio(text=text)

        # Store audio in cloud storage
        storage_key = f"audio/{uuid.uuid4()}.mp3"
        await storage_client.save(
            key=storage_key,
            data=audio_bytes,
            mimetype="audio/mpeg"
        )

        # Generate pre-signed URL (valid for 7 days)
        url = await storage_client.get_pre_signed_url(
            key=storage_key,
            expires_in=3600 * 24 * 7
        )

        logger.info(f"TTS audio generated successfully: {storage_key}")
        return {
            "status": "success",
            "content": [
                {
                    "text": url
                }
            ]
        }
    except Exception as e:
        logger.error(f"TTS generation failed: {type(e).__name__}: {e}")
        raise e


dou_bao_tts_router.register(dou_bao_text_to_speech)