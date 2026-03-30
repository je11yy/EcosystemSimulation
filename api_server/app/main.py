from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.db.init_models  # type: ignore # noqa: F401
from app.api.genome_templates import router as genome_templates_router
from app.api.health import router as health_router
from app.api.simulations import router as simulations_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.simulation_runtime_manager import SimulationRuntimeManager


def create_app() -> FastAPI:
    runtime_manager = SimulationRuntimeManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        await runtime_manager.stop_all()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.simulation_runtime_manager = runtime_manager

    app.include_router(health_router)
    app.include_router(simulations_router)
    app.include_router(genome_templates_router)

    return app


app = create_app()
