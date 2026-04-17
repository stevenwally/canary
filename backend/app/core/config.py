from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://canary:canary@localhost:5432/canary"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"
    APP_ENV: str = "development"

    # Reddit (via asyncpraw)
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "canary:v0.1.0 (sentiment analysis)"

    # NewsAPI
    NEWSAPI_KEY: str = ""

    # Bluesky (AT Protocol) - no auth required for public search
    BLUESKY_API_URL: str = "https://public.api.bsky.app"

    @property
    def database_url_sync(self) -> str:
        """Sync database URL for Alembic migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")


settings = Settings()
