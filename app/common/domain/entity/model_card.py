from __future__ import annotations

from typing import List, Optional

from litellm import provider_list, LITELLM_CHAT_PROVIDERS
from litellm.types.utils import LlmProviders
from pydantic import BaseModel, Field




class ModelCard(BaseModel):
    id: str = Field(..., description="model id used in API calls (e.g. gpt-4o)")
    name: str = Field(..., description="human-readable model name")
    max_tokens: Optional[int] = Field(
        default=4096, description="maximum number of output tokens"
    )
    context_window: Optional[int] = Field(
        default=16384, description="maximum context window size"
    )
    description: str = Field(..., description="human readable model description")
    enabled: bool = Field(
        default=True, description="whether this model is enabled"
    )
    provider_id: Optional[str] = Field(
        default=None, description="id of the provider this model belongs to"
    )


class ProviderCard(BaseModel):
    id: str = Field(..., description="provider id used in API calls (e.g. openai)")
    name: str = Field(..., description="human-readable provider name")
    family: str = Field(..., description="family (e.g. openai, anthropic)")
    base_url: Optional[str] = Field(default=None, description="provider url")
    api_key: Optional[str] = Field(default=None, description="provider url")
    enabled: bool = False
    priority: int = Field(
        default=100,
        description="provider priority for fallback (lower number = higher priority)"
    )
    models: List[ModelCard] = Field(default_factory=list)

    def model_post_init(self, __context):
        if self.family not in LITELLM_CHAT_PROVIDERS:
            raise ValueError(
                f"id must be one of {LITELLM_CHAT_PROVIDERS!r}, got {self.family!r}"
            )
        for m in self.models:
            if m.provider_id and m.provider_id != self.id:
                raise ValueError(
                    f"model '{m.id}' provider_id='{m.provider_id}' "
                    f"does not match its parent provider '{self.id}'"
                )
            m.provider_id = self.id

