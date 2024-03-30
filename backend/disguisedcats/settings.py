from typing import Literal
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOSTNAME: str
    PORT: int = 8000

    DB_URL: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr

    STATIC_PATH: Path

    PEERJS_HOST: str = "/"
    PEERJS_PORT: int = 80
    PEERJS_PATH: str = "/peer"

    LOG_LEVEL: Literal["DEBUG", "INFO"] = "INFO"

    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
