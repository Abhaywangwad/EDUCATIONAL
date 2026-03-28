import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Human-Like Grading System"
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "data")
    database_path: Path | None = None
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    llm_provider: str = "mock"
    llm_api_key: str = ""
    openai_api_key: str = Field(default="", validation_alias=AliasChoices("OPENAI_API_KEY"))
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-5-mini"
    semantic_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_prefix="HLGS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_origins")
    @classmethod
    def ensure_local_origins(cls, value: list[str]) -> list[str]:
        normalized = list(dict.fromkeys(value))
        for origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
            if origin not in normalized:
                normalized.append(origin)
        return normalized

    @property
    def resolved_database_path(self) -> Path:
        if self.database_path is not None:
            return self.database_path
        return self.data_dir / "hlgs.db"

    @property
    def resolved_llm_api_key(self) -> str:
        raw_value = self.llm_api_key or self.openai_api_key or os.getenv("OPENAI_API_KEY", "")
        return "".join(character for character in raw_value.strip() if character.isprintable())

    @property
    def resolved_llm_base_url(self) -> str:
        return os.getenv("OPENAI_BASE_URL", self.llm_base_url)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
