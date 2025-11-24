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
        """严格查找模型：只在指定的 provider 中查找，找不到直接抛异常"""
        if provider_id is None:
            provider_id = self.default_provider
        provider = self.providers.get(provider_id)
        if not provider or not provider.enabled:
            raise KeyError(f"provider '{provider_id}' not found or disabled")
        for m in provider.models:
            if m.id == model_id and m.enabled:
                return m
        raise KeyError(f"model '{model_id}' not found or disabled under provider '{provider_id}'")

    def find_model_with_fallback(self, model_id: str, provider_id: Optional[str] = None) -> ModelCard:
        """智能查找模型：优先在指定 provider 查找，找不到则按优先级在其他 enabled providers 中查找

        Args:
            model_id: 模型 ID
            provider_id: 优先查找的 provider ID（默认为 default_provider）

        Returns:
            找到的 ModelCard，provider_id 字段已设置为实际找到的 provider

        Raises:
            KeyError: 所有 enabled providers 中都找不到该模型
        """
        # 1. 优先在指定的 provider 中查找
        target_provider_id = provider_id or self.default_provider
        try:
            return self.find_model(model_id, target_provider_id)
        except KeyError:
            pass

        # 2. 在其他 enabled 的 providers 中按优先级查找
        enabled_providers = [
            (p_id, provider)
            for p_id, provider in self.providers.items()
            if provider.enabled and p_id != target_provider_id
        ]

        # 按 priority 排序（数字越小优先级越高）
        enabled_providers.sort(key=lambda x: x[1].priority)

        for p_id, provider in enabled_providers:
            for m in provider.models:
                if m.id == model_id and m.enabled:
                    return m

        # 3. 所有 providers 都找不到，抛出异常
        raise KeyError(
            f"model '{model_id}' not found in any enabled providers "
            f"(tried: {target_provider_id} and {len(enabled_providers)} fallback providers)"
        )

    def get_active_provider(self, provider_id: Optional[str] = None) -> ProviderCard:
        if provider_id is None:
            provider_id = self.default_provider
        provider = self.providers.get(provider_id)
        if not provider or not provider.enabled:
            raise KeyError(f"provider '{provider_id}' not found or disabled")
        return provider

    def get_all_models(self, provider_id: Optional[str] = None) -> list[ModelCard]:
        """Get all models from provider(s).

        Args:
            provider_id:
                - None: 返回所有 enabled providers 的所有模型
                - str: 只返回指定 provider 的模型

        Returns:
            模型列表，按 provider priority 排序
        """
        if provider_id is not None:
            # 指定了 provider，只返回该 provider 的 enabled 模型
            provider = self.providers.get(provider_id)
            if not provider or not provider.enabled:
                raise KeyError(f"provider '{provider_id}' not found or disabled")
            return [m for m in provider.models if m.enabled]

        # 未指定 provider，返回所有 enabled providers 的 enabled 模型
        all_models = []
        enabled_providers = [
            (p_id, provider)
            for p_id, provider in self.providers.items()
            if provider.enabled
        ]

        # 按 priority 排序
        enabled_providers.sort(key=lambda x: x[1].priority)

        for p_id, provider in enabled_providers:
            all_models.extend([m for m in provider.models if m.enabled])

        return all_models

    def format_models_for_prompt(self) -> str:
        """格式化所有可用模型为 LLM 提示词

        Returns:
            格式化的列表字符串，格式：
            - model_id: description [provider: provider_id]
            注意：provider 信息放在描述末尾，避免 LLM 混淆 model_id
        """
        models = self.get_all_models()
        if not models:
            return "None available"

        lines = [
            f"- {model.id}: {model.description} [provider: {model.provider_id}]"
            for model in models
        ]
        return "\n".join(lines)

    @classmethod
    def parse_toml(cls, path: str | Path) -> ModelCardManager:
        data = tomllib.loads(Path(path).read_text())
        return cls.model_validate(data)


model_card_manager: ModelCardManager = ModelCardManager.parse_toml(
    Constants.Path.MODELS_TOML
)
