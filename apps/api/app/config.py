from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_cors_origins: str = "http://localhost:3000"
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    n8n_base_url: str = ""
    n8n_api_key: str = ""
    n8n_webhook_base_url: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    clerk_secret_key: str = ""
    mock_user_id: str = Field(default="local-demo-user")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def n8n_enabled(self) -> bool:
        return bool(self.n8n_base_url and self.n8n_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()

