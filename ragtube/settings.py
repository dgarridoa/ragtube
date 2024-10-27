from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    youtube_api_key: SecretStr
    db_user: SecretStr
    db_password: SecretStr
    db_host: SecretStr
    db_port: SecretStr
    db_name: SecretStr
    api_user: SecretStr
    api_password: SecretStr
    api_host: SecretStr
    api_port: SecretStr


@lru_cache
def get_settings():
    settings = Settings()  # type: ignore
    return settings
