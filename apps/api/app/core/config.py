"""
config.py — Application Settings (Phase 5)
===========================================
WHAT THIS DOES:
  Reads environment variables from `.env` file and converts them into
  typed Python objects.

PHASE 5 ADDITIONS:
  - LLM Provider Configuration: OpenAI, Anthropic, Google Gemini, Ollama, & Local Fallback.
  - Model & Temperature settings for deterministic enterprise RAG answering.
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App Config ---
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origins: str = "http://localhost:3000"

    # --- Auth & JWT Config ---
    jwt_secret: str = Field(
        default="multimind-super-secret-jwt-key-for-dev-environment-12345",
        min_length=16,
        description="Secret key for signing JSON Web Tokens",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # --- Vector DB & RAG Config (Phase 4) ---
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "enterprise_knowledge"
    vector_dimension: int = 384

    # --- LLM Gateway Config (Phase 5) ---
    default_llm_provider: str = "openai"  # "openai" | "anthropic" | "gemini" | "ollama" | "local"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2

    @property
    def cors_origins(self) -> list[str]:
        """Split comma-separated origins into a list."""
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
