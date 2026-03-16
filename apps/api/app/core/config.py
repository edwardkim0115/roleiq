from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RoleIQ API"
    database_url: str = Field(
        default="postgresql+psycopg://roleiq:roleiq@localhost:5432/roleiq",
        alias="DATABASE_URL",
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_parser_model: str = Field(default="gpt-4.1", alias="OPENAI_PARSER_MODEL")
    openai_suggestion_model: str = Field(default="gpt-4.1", alias="OPENAI_SUGGESTION_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    max_upload_size_mb: int = Field(default=10, alias="MAX_UPLOAD_SIZE_MB")
    request_timeout_seconds: float = 45.0

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
