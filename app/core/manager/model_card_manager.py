#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2025/6/28
# @Author  : .*?
# @Email   : amashiro2233@gmail.com
# @File    : model_card_manager
# @Software: PyCharm
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel

from app.common.constants.constants import Constants
from app.common.domain.entity.model_card import ProviderCard, ModelCard


class ModelCardManager(BaseModel):
    default_provider: str
    providers: Dict[str, ProviderCard]

    def model_post_init(self, __context):
        if self.default_provider not in self.providers:
            raise ValueError(
                f"default_provider '{self.default_provider}' "
                f"not found in providers list"
            )
        if not self.providers[self.default_provider].enabled:
            raise ValueError(
                f"default_provider '{self.default_provider}' is not enabled"
            )

    def find_model(self, model_id: str, provider_id: Optional[str] = None) -> ModelCard:
        if provider_id is None:
            provider_id = self.default_provider
        provider = self.providers.get(provider_id)
        if not provider or not provider.enabled:
            raise KeyError(f"provider '{provider_id}' not found or disabled")
        for m in provider.models:
            if m.id == model_id:
                return m
        raise KeyError(f"model '{model_id}' not found under provider '{provider_id}'")

    def get_active_provider(self, provider_id: Optional[str] = None) -> ProviderCard:
        if provider_id is None:
            provider_id = self.default_provider
        provider = self.providers.get(provider_id)
        if not provider or not provider.enabled:
            raise KeyError(f"provider '{provider_id}' not found or disabled")
        return provider

    def get_all_models(self, provider_id: Optional[str] = None) -> list[ModelCard]:
        """Get all models from a provider (defaults to default_provider)."""
        if provider_id is None:
            provider_id = self.default_provider
        provider = self.providers.get(provider_id)
        if not provider or not provider.enabled:
            raise KeyError(f"provider '{provider_id}' not found or disabled")
        return provider.models

    @classmethod
    def parse_toml(cls, path: str | Path) -> ModelCardManager:
        data = tomllib.loads(Path(path).read_text())
        return cls.model_validate(data)


model_card_manager: ModelCardManager = ModelCardManager.parse_toml(
    Constants.Path.MODELS_TOML
)
if __name__ == '__main__':
    for model in model_card_manager.get_all_models():
        print(model.model_dump_json(indent=2))