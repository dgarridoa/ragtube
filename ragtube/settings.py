import os
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from ragtube import PROJECT_DIR


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(PROJECT_DIR, ".env"), env_file_encoding="utf-8"
    )

    youtube_api_key: SecretStr
    https_proxy: SecretStr | None = None
    db_user: SecretStr
    db_password: SecretStr
    db_host: SecretStr
    db_port: SecretStr
    db_name: SecretStr
    api_host: SecretStr
    api_port: SecretStr


@lru_cache
def get_settings():
    settings = Settings()  # type: ignore
    return settings
