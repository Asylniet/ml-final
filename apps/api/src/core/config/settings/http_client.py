from typing import ClassVar

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config.settings.base import BaseSettings


class HttpClientSettings(BaseSettings):
    base_url: str
    timeout: float = Field(default=30.0)
    headers: dict[str, str] = Field(default_factory=dict)


class CommonsHttpClientSettings(HttpClientSettings):
    model_config: ClassVar[SettingsConfigDict] = HttpClientSettings.model_config | {
        "env_prefix": "COMMONS_",
    }

class AccountsHttpClientSettings(HttpClientSettings):
    model_config: ClassVar[SettingsConfigDict] = HttpClientSettings.model_config | {
        "env_prefix": "ACCOUNTS_",
    }
