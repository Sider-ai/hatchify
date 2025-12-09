import os
from functools import lru_cache
from pathlib import Path
from typing import Type, Tuple, Optional, Any, Annotated, Literal, List, Union, Dict

from pydantic import Field, BaseModel, model_validator, BeforeValidator, computed_field
from pydantic_settings import (
    PydanticBaseSettingsSource,
    BaseSettings,
    YamlConfigSettingsSource,
    SettingsConfigDict,
)

from hatchify.common.constants.constants import Constants
from hatchify.common.domain.enums.db_type import DatabasePlatform
from hatchify.common.domain.enums.session_manager_type import SessionManagerType
from hatchify.common.domain.enums.storage_type import StorageType


def resolve_path(v: str | Path | None) -> str | None:
    if v is None:
        return None
    path = Path(v).expanduser()
    if not path.is_absolute():
        path = Path(Constants.Path.RootPath) / path
    return path.resolve().as_posix()


ResolvablePath = Annotated[str | None, BeforeValidator(resolve_path)]


class EnvSettings(BaseSettings):
    environment: str = Field(default="dev", validation_alias="ENVIRONMENT")

    model_config = SettingsConfigDict(
        env_file=Constants.Path.EnvPath if os.path.exists(Constants.Path.EnvPath) else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def yaml_path(self) -> str:
        return Constants.Path.get_yaml_path(self.environment)


_env_settings = EnvSettings()


class ServerSettings(BaseSettings):
    host: str
    port: int
    base_url: str


class ProviderSettings(BaseSettings):
    model: str
    provider: Optional[str] = Field(default=None)


class ModelSettings(BaseSettings):
    """不同用途的模型配置"""
    web_builder: ProviderSettings = Field(
        ...,
        description="Web构建者的模型"
    )
    spec_generator: ProviderSettings = Field(
        ...,
        description="用于生成 GraphSpec 架构的模型"
    )
    schema_extractor: ProviderSettings = Field(
        ...,
        description="用于从 Agent Instructions 提取 JSON Schema 的模型"
    )


class OpenDal(BaseModel):
    opendal_schema: str | None = Field(default="fs")
    bucket: str
    folder: str | None
    root: ResolvablePath = None


class StorageSettings(BaseModel):
    platform: StorageType

    opendal: OpenDal | None

    @model_validator(mode='before')
    def clear_conflicting_settings(self):
        for key in [member for member in StorageType if member != self['platform']]:
            self[key] = None
        return self


class FileManagerSettings(BaseSettings):
    folder: str | None
    root: ResolvablePath = None


class SessionManagerSettings(BaseSettings):
    manager: SessionManagerType
    file: FileManagerSettings | None = Field(default=None)


class SqliteSettings(BaseModel):
    driver: str = Field(default="sqlite+aiosqlite")
    file: ResolvablePath = None
    echo: bool = Field(default=False)
    pool_pre_ping: bool = Field(default=True)
    connect_args: dict[str, Any] = Field(
        default_factory=dict,
    )

    @computed_field
    @property
    def url(self) -> str:
        """生成完整的 SQLite 连接 URL"""
        if self.file is None:
            raise ValueError("SQLite file path is required")
        # sqlite+aiosqlite:////absolute/path/to/db.sqlite
        return f"{self.driver}:///{self.file}"


class DbSettings(BaseModel):
    platform: DatabasePlatform
    sqlite: SqliteSettings | None = None

    @model_validator(mode="before")
    def clear_conflicting_settings(cls, values: dict):
        platform = values.get("platform")
        if platform != "sqlite":
            values["sqlite"] = None
        return values


class EnvStep(BaseModel):
    """写入环境变量文件"""
    type: Literal["env"] = "env"
    file: str | None = None
    vars: Dict[str, Any] = Field(default_factory=dict)


class WriteInputSchemaStep(BaseModel):
    """写入输入 schema 文件"""
    type: Literal["write_input_schema"] = "write_input_schema"
    file: str | None = None


class WriteOutputSchemaStep(BaseModel):
    """写入输出 schema 文件"""
    type: Literal["write_output_schema"] = "write_output_schema"
    file: str | None = None


class SecuritySettings(BaseModel):
    allowed_directories: List[str] = Field(default_factory=list)
    sensitive_paths: List[str] = Field(default_factory=list)


class WebAppBuilderSettings(BaseSettings):
    repo_url: str
    branch: str = Field(default="master")
    workspace: ResolvablePath = None
    init_steps: List[Union[EnvStep | WriteInputSchemaStep | WriteOutputSchemaStep]] | None = Field(default=None)
    security: SecuritySettings | None = Field(default=None)

class HatchifySettings(BaseModel):
    application: str
    server: ServerSettings | None = Field(default=None)
    models: ModelSettings | None = Field(default=None)
    storage: StorageSettings | None = Field(default=None)
    session_manager: SessionManagerSettings | None = Field(default=None)
    db: DbSettings | None = Field(default=None)
    web_app_builder: WebAppBuilderSettings | None = Field(default=None)


class AppSettings(BaseSettings):
    hatchify: HatchifySettings | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file=_env_settings.yaml_path,
                yaml_file_encoding="utf-8",
            ),
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_hatchify_settings():
    app_settings = AppSettings()
    return app_settings.hatchify


if __name__ == '__main__':
    print(get_hatchify_settings())
