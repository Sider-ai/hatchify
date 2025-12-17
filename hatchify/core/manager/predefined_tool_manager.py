from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field, model_validator

from hatchify.common.constants.constants import Constants


class BasePreDefinedToolCard(BaseModel):
    enabled: bool = Field(default=False, description="Whether this tool is enabled")


class NanoBananaCardPreDefined(BasePreDefinedToolCard):
    model: str = Field(
        default="gemini-3-pro-image-preview",
        description="Gemini model name for image generation",
    )
    api_key: Optional[str] = Field(default=None, description="Google Generative AI API key")

    @model_validator(mode="after")
    def validate_enabled_config(self):
        """Validate required fields when enabled"""
        if self.enabled:
            if not self.api_key or self.api_key.strip() == "":
                raise ValueError(
                    "nano_banana: api_key is required when enabled=true"
                )
        return self


class PreDefinedToolsConfig(BaseModel):
    nano_banana: Optional[NanoBananaCardPreDefined] = None


class PreDefinedToolManager(BaseModel):
    config: PreDefinedToolsConfig

    @classmethod
    def parse_toml(cls, path: str | Path) -> PreDefinedToolManager:
        path = Path(path)

        if not path.exists():
            logger.warning(f"Predefined tools config not found: {path}")
            return cls(config=PreDefinedToolsConfig())

        try:
            data = tomllib.loads(path.read_text())

            tools_config = PreDefinedToolsConfig.model_validate(data)
            return cls(config=tools_config)

        except Exception as e:
            logger.error(f"Failed to parse predefined tools config: {e}")
            return cls(config=PreDefinedToolsConfig())


@lru_cache
def get_pre_defined_tool_configs() -> PreDefinedToolsConfig:
    pre_defined_tool_manager: PreDefinedToolManager = PreDefinedToolManager.parse_toml(
        Constants.Path.ToolsToml
    )
    return pre_defined_tool_manager.config
