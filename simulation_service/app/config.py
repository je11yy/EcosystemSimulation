from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    runtime_step_interval_seconds: float = 1.0


settings = Settings()
