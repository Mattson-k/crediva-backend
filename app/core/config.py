from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_title: str = "Crediva API"
    api_version: str = "0.1.0"
    database_url: str = "sqlite:///./crediva.db"
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    frontend_api_base_url: str = ""
    static_cache_seconds: int = 3600
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def parsed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
