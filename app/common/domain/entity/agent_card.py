from typing import Optional, List

from pydantic import BaseModel, Field, computed_field, ConfigDict

from app.common.domain.entity.model_card import ModelCard
from app.core.manager.model_card_manager import model_card_manager


class AgentCard(BaseModel):
    name: str
    model: str
    instruction: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    tools: List[str] = Field(default_factory=list)

    # custom agent card config
    provider: Optional[str] = Field(
        default=None, description="custom model provider, if needed"
    )
    base_url: Optional[str] = Field(
        default=None, description="custom model base_url, if needed"
    )
    api_key: Optional[str] = Field(
        default=None, description="custom model api_key, if needed"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="custom model max output tokens, if needed"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @computed_field
    @property
    def model_card(self) -> ModelCard:
        return model_card_manager.find_model(self.model, self.provider)
