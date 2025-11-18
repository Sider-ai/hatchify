from strands.models import Model
from strands.models.litellm import LiteLLMModel

from app.common.domain.entity.agent_card import AgentCard
from app.common.domain.entity.model_card import ModelCard
from app.core.manager.model_card_manager import model_card_manager


def create_llm_by_model_card(model_card: ModelCard) -> Model:
    provider_card = model_card_manager.get_active_provider(model_card.provider_id)

    base_url = provider_card.base_url
    api_key = provider_card.api_key

    return LiteLLMModel(
        client_args={
            "api_key": api_key,
            "base_url": base_url,
        },
        model_id=f"{provider_card.family}/{model_card.id}",
        params={
            "max_completion_tokens": model_card.max_tokens,
        }
    )


def create_llm_by_agent_card(agent_card: AgentCard) -> Model:
    model_card = model_card_manager.find_model(agent_card.model, agent_card.provider)
    provider_card = model_card_manager.get_active_provider(model_card.provider_id)

    if agent_card.base_url:
        base_url = agent_card.base_url
        api_key = agent_card.api_key
    else:
        base_url = provider_card.base_url
        api_key = provider_card.api_key
    max_tokens = agent_card.max_tokens or model_card.max_tokens
    return LiteLLMModel(
        client_args={
            "api_key": api_key,
            "base_url": base_url,
        },
        model_id=f"{provider_card.family}/{model_card.id}",
        params={
            "max_completion_tokens": max_tokens,
        }
    )
