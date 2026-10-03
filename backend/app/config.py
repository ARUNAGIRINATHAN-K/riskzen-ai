from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Environment ──
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://riskzen:riskzen_dev@db:5432/riskzen"
    DATABASE_URL_SYNC: str = "postgresql://riskzen:riskzen_dev@db:5432/riskzen"

    # ── API Security ──
    API_KEY: str = "riskzen-dev-key"

    # ── Encryption ──
    ENCRYPTION_KEY: str = ""

    # ── GitHub ──
    GITHUB_TOKEN: str = ""

    # ── LLM ──
    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3.1"
    OLLAMA_HOST: str = "http://ollama:11434"
    OPENAI_API_KEY: str = ""

    # ── Scheduler ──
    SYNC_INTERVAL_MINUTES: int = 60

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()
