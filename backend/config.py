from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    api_cors_origins: str = "http://localhost:3000"
    database_url: str = ""
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
    clerk_jwt_issuer: str = ""
    database_url: str = ""
    mock_user_id: str = Field(default="local-demo-user")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() == "production"

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)

    @property
    def database_configured(self) -> bool:
        return bool(self.database_url.strip())

    @property
    def auth_enabled(self) -> bool:
        return bool(self.clerk_secret_key and self.clerk_jwt_issuer)

    @property
    def n8n_enabled(self) -> bool:
        return bool(self.n8n_base_url and self.n8n_api_key)

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return "sqlite:///./automation.db"

    def production_issues(self) -> list[str]:
        if not self.is_production:
            return []

        issues: list[str] = []
        if not self.auth_enabled:
            issues.append("Set CLERK_SECRET_KEY and CLERK_JWT_ISSUER for production auth.")
        if not self.database_configured:
            issues.append("Set DATABASE_URL for PostgreSQL persistence.")
        if any("localhost" in origin or "127.0.0.1" in origin for origin in self.cors_origins):
            issues.append("API_CORS_ORIGINS should list your production frontend URL, not localhost.")
        return issues


@lru_cache
def get_settings() -> Settings:
    return Settings()
