from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sourcing:sourcing@db:5432/sourcing"
    sync_database_url: str = "postgresql://sourcing:sourcing@db:5432/sourcing"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Adapter selection
    llm_adapter: str = "mock"
    source_adapters: str = "mock,github,stackoverflow,duckduckgo"
    contact_adapter: str = "mock"
    outreach_whatsapp_adapter: str = "mock"
    outreach_email_adapter: str = "mock"
    telephony_adapter: str = "mock"
    interview_adapter: str = "mock"
    embedding_adapter: str = "mock"

    # Optional API keys (all None in Phase 1)
    github_token: str | None = None
    stackoverflow_key: str | None = None
    juicebox_api_key: str | None = None
    apollo_api_key: str | None = None
    anthropic_api_key: str | None = None
    gupshup_api_key: str | None = None
    gupshup_app_id: str | None = None
    gupshup_source_number: str | None = None
    plivo_auth_id: str | None = None
    plivo_auth_token: str | None = None
    plivo_source_number: str | None = None

    outreach_escalation_hours: int = 48
    default_retention_days: int = 90
    default_contact_reveal_enabled: bool = False

    @property
    def source_adapter_list(self) -> List[str]:
        return [s.strip() for s in self.source_adapters.split(",") if s.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
