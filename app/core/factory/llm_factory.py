import asyncio

from strands.models import Model
from strands.models.litellm import LiteLLMModel
from strands.types.content import Messages, Message, ContentBlock

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


if __name__ == '__main__':
    async def test_llm(system_prompt: str, messages: Messages):
        model = create_llm_by_model_card(model_card_manager.find_model(provider_id="openai-like", model_id="gpt-4o"))
        async for chunk in model.stream(system_prompt=system_prompt, messages=messages):
            print(chunk)


    asyncio.run(
        test_llm(
            system_prompt="You are an AI that is helpful to humans.",
            messages=[
                Message(
                    role="user",
                    content=[
                        ContentBlock(
                            text="你好啊，你是什么AI"
                        )
                    ]
                )
            ]
        )
    )
