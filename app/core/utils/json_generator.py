"""JSON 结构化输出生成器

使用 Instructor + LiteLLM 生成结构化的 JSON 输出，支持自动重试和错误修正。
"""

from typing import Type, TypeVar, List, Dict, Any, Union, Iterable, Optional, Tuple

import instructor
from instructor import Partial
from litellm import acompletion
from litellm.types.completion import ChatCompletionMessageParam
from litellm.types.utils import ModelResponse, Usage
from pydantic import BaseModel

from app.core.manager.model_card_manager import model_card_manager

T = TypeVar("T", bound=Union[BaseModel, "Iterable[Any]", "Partial[Any]"])


async def json_generator(
        provider_id: str,
        model_id: str,
        messages: List[ChatCompletionMessageParam],
        response_model: Type[T],
        mode: instructor.Mode = instructor.Mode.JSON,
        max_retries: int = 3,
        return_usage: bool = False,
        **kwargs: Any,
) -> Tuple[T, Optional[Usage]]:
    """
    生成结构化 JSON 输出。

    使用 Instructor 提供自动重试和错误修正能力，确保高成功率。

    Args:
        provider_id: 提供商 ID (如 "google", "openai")
        model_id: 模型 ID (如 "gemini-2.5-pro", "gpt-4o")
        messages: 消息列表，格式: [{"role": "user", "content": "..."}]
        response_model: Pydantic 模型类
        mode: Instructor 模式（默认 JSON mode，兼容性最好）
        max_retries: 最大重试次数（默认 3 次）
        return_usage: 是否同时返回 token 用量信息 (tuple: model, usage)
        **kwargs: 其他 LiteLLM 参数

    Returns:
        验证后的 Pydantic 模型实例；如果 return_usage=True，返回 (model, usage)

    Example:
        ```python
        from app.common.domain.entity.graph_generation_output import SchemaExtractionOutput

        result = await json_generator(
            provider_id="google",
            model_id="gemini-2.5-pro",
            messages=[
                {"role": "system", "content": "You are an expert."},
                {"role": "user", "content": "Extract schema..."}
            ],
            response_model=SchemaExtractionOutput,
            max_retries=3,
        )
        ```
    """
    usage: Optional[Usage] = None
    # 获取配置
    model_card = model_card_manager.find_model(model_id, provider_id)
    provider_card = model_card_manager.get_active_provider(model_card.provider_id)

    # 创建 Instructor 客户端
    client = instructor.from_litellm(acompletion, mode=mode)

    # 构建调用参数
    call_kwargs: Dict[str, Any] = {
        "max_tokens": model_card.max_tokens,
        **kwargs,
    }
    if provider_card.api_key:
        call_kwargs["api_key"] = provider_card.api_key
    if provider_card.base_url:
        call_kwargs["api_base"] = provider_card.base_url

    # 调用 Instructor
    result = await client.chat.completions.create(
        model=f"{provider_card.family}/{model_card.id}",
        messages=messages,
        response_model=response_model,
        max_retries=max_retries,
        return_usage=True,
        **call_kwargs,
    )

    if not return_usage:
        return result, usage

    raw_response: ModelResponse = getattr(result, "_raw_response", None)
    if raw_response is not None:
        usage: Usage = getattr(raw_response, "usage", None)

    return result, usage
