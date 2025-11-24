from typing import Optional, Union, Type, Dict, Any

from pydantic import BaseModel
from strands.models import Model
from strands.models.gemini import GeminiModel
from strands.models.litellm import LiteLLMModel
from strands.models.openai import OpenAIModel

from app.common.domain.entity.agent_card import AgentCard
from app.common.domain.entity.model_card import ModelCard
from app.core.manager.model_card_manager import model_card_manager


def create_llm_by_model_card(
        model_card: ModelCard,
        response_format: Optional[Union[dict, Type[BaseModel]]] = None,
) -> Model:
    """
    创建 LLM 实例。

    Args:
        model_card: 模型配置卡片
        response_format: 响应格式配置
            - {"type": "json_object"}: 启用 JSON mode，LLM 返回 JSON 字符串
            - Pydantic BaseModel: 启用 structured output（注意 Gemini 不支持动态类型）

    Returns:
        LiteLLMModel 实例
    """
    provider_card = model_card_manager.get_active_provider(model_card.provider_id)

    base_url = provider_card.base_url
    api_key = provider_card.api_key

    # 如果指定了 response_format，添加到 params
    # 注意：不同 provider 使用不同的参数名称
    match provider_card.family:
        case "openai":
            params = {
                "max_completion_tokens": model_card.max_tokens,
            }
            if response_format is not None:
                params["response_format"] = response_format
            return OpenAIModel(
                client_args={
                    "api_key": api_key,
                    "base_url": base_url,
                },
                model_id=model_card.id,
                params=params
            )
        case "gemini":
            # Gemini 使用 max_output_tokens 而不是 max_completion_tokens
            params = {
                "max_output_tokens": model_card.max_tokens,
            }
            # Gemini 不支持 response_format 参数（使用 response_schema 替代）
            return GeminiModel(
                client_args={
                    "api_key": api_key,
                    "base_url": base_url,
                },
                model_id=model_card.id,
                params=params
            )
        case _:
            return LiteLLMModel(
                client_args={
                    "api_key": api_key,
                    "base_url": base_url,
                },
                model_id=f"{provider_card.family}/{model_card.id}",
                params=params
            )


def create_llm_by_agent_card(agent_card: AgentCard) -> Model:
    """
    创建 LLM 实例，支持灵活的参数覆盖策略。

    覆盖优先级: agent 配置 > provider 配置 > None (由 LiteLLM 处理)

    注意: 如果 base_url 为 None，则必须提供 api_key（标准云服务）
          如果有 base_url，则 api_key 可以为 None（本地服务、私有服务）

    +------------------+---------------------+---------------------+---------------------------------------+
    | 场景             | Agent               | Provider            | 最终结果                              |
    +------------------+---------------------+---------------------+---------------------------------------+
    | 完全覆盖         | base_url + api_key  | base_url + api_key  | 使用 agent 的配置                     |
    | 部分覆盖 base_url | base_url            | api_key             | agent.base_url + provider.api_key    |
    | 部分覆盖 api_key  | api_key             | base_url            | provider.base_url + agent.api_key    |
    | 标准云服务       | -                   | api_key (无 base_url)| 只传 api_key，由 LiteLLM 处理 URL    |
    | Ollama 本地      | -                   | base_url (无 api_key)| 只传 base_url                        |
    | 私有服务         | base_url (无 api_key)| -                   | 只传 agent.base_url                  |
    +------------------+---------------------+---------------------+---------------------------------------+
    """
    # 使用 fallback 机制：优先在指定 provider 查找，找不到则按优先级在其他 enabled providers 中查找
    model_card = model_card_manager.find_model_with_fallback(agent_card.model, agent_card.provider)
    provider_card = model_card_manager.get_active_provider(model_card.provider_id)

    # 灵活的参数覆盖逻辑：agent 优先，否则使用 provider，都没有则为 None
    # agent.base_url 优先于 provider.base_url
    base_url = agent_card.base_url if agent_card.base_url is not None else provider_card.base_url

    # agent.api_key 优先于 provider.api_key
    api_key = agent_card.api_key if agent_card.api_key is not None else provider_card.api_key

    # 验证配置有效性：如果没有 base_url，则必须有 api_key
    if base_url is None and api_key is None:
        raise ValueError(
            f"Invalid LLM configuration for agent '{agent_card.name}': "
            f"Either base_url or api_key must be provided. "
            f"For standard cloud services (OpenAI, Anthropic, etc.), provide api_key. "
            f"For local/private services (Ollama, etc.), provide base_url."
        )

    # max_tokens 覆盖逻辑
    max_tokens = agent_card.max_tokens or model_card.max_tokens

    # 构建 client_args，只包含非 None 的参数
    client_args = {}
    if api_key is not None:
        client_args["api_key"] = api_key
    if base_url is not None:
        client_args["base_url"] = base_url

    # 根据 provider family 选择合适的 Model 实现
    # 注意：不同 provider 使用不同的参数名称
    match provider_card.family:
        case "openai":
            params = {
                "max_completion_tokens": max_tokens,
            }
            return OpenAIModel(
                client_args=client_args,
                model_id=model_card.id,
                params=params
            )
        case "gemini":
            # 使用 GeminiModel 原生支持 Gemini 特性（包括 thinking mode 和 reasoningContent）
            # Gemini 使用 max_output_tokens 而不是 max_completion_tokens
            params = {
                "max_output_tokens": max_tokens,
            }
            return GeminiModel(
                client_args=client_args,
                model_id=model_card.id,
                params=params
            )
        case _:
            # 其他 provider 使用 LiteLLMModel
            params = {
                "max_completion_tokens": max_tokens,
            }
            return LiteLLMModel(
                client_args=client_args,
                model_id=f"{provider_card.family}/{model_card.id}",
                params=params
            )
