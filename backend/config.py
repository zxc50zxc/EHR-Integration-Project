import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ehr.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars!!")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    ENCRYPTION_KEY: str | None = os.getenv("ENCRYPTION_KEY")

    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
