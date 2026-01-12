from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    github_token: str | None = Field(default=None, alias="GITHUB_TOKEN")
    regulus_data_dir: Path = Field(default=Path("./data"), alias="REGULUS_DATA_DIR")
    regulus_allowed_roots: list[Path] = Field(
        default_factory=lambda: [Path(".")], alias="REGULUS_ALLOWED_ROOTS"
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"], alias="CORS_ORIGINS"
    )
    log_level: str = Field(default="info", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("regulus_allowed_roots", mode="before")
    @classmethod
    def parse_allowed_roots(cls, value: object) -> list[Path]:
        if isinstance(value, list):
            return [Path(str(item)) for item in value]
        if isinstance(value, str):
            return [Path(item.strip()) for item in value.split(",") if item.strip()]
        return [Path(".")]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
