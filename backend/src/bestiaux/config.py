from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://bestiaux:bestiaux@localhost:5432/bestiaux"
    session_secret_key: str = "change-me-in-production"
    session_max_age_seconds: int = 60 * 60 * 24 * 7  # 7 days

    model_config = {"env_prefix": "BESTIAUX_"}


settings = Settings()
