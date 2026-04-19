from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    runtime_step_interval_seconds: float = 1.0
    runtime_completed_results_limit: int = 1000


settings = Settings()
