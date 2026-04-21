from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "ecosim"
    postgres_user: str = "ecosim"
    postgres_password: str = "ecosim"
    simulation_service_base_url: str = "http://simulation-service:8001"
    app_debug: bool = False
    auth_secret_key: str = "change-me-in-production"
    auth_token_ttl_seconds: int = 60 * 60 * 24 * 7
    auth_cookie_name: str = "ecosim_session"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @cached_property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def debug(self) -> bool:
        return self.app_debug


settings = Settings()
