from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.runtime_routes import build_runtime_router
from app.core.config import settings
from app.services.engine_factory import EngineFactory
from app.services.runtime_manager import RuntimeManager


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    runtime_manager = RuntimeManager()
    engine_factory = EngineFactory()

    app.state.runtime_manager = runtime_manager
    app.state.engine_factory = engine_factory

    app.include_router(health_router)
    app.include_router(build_runtime_router(runtime_manager, engine_factory))

    return app


app = create_app()
