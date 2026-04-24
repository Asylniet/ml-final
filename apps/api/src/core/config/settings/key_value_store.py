from typing import ClassVar

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config.settings.base import BaseSettings


class KeyValueStoreSettings(BaseSettings):
    host: str
    port: int
    user: str | None = Field(default=None)
    password: str | None = Field(default=None)
    db: str

    model_config: ClassVar[SettingsConfigDict] = BaseSettings.model_config | {
        "env_prefix": "KEY_VALUE_STORE_",
    }
