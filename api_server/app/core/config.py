from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EcoSim API Server"
    debug: bool = True

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "ecosim"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    simulation_service_base_url: str = "http://simulation-service:8001"

    simulation_step_interval_seconds: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
