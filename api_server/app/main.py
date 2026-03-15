from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.db.init_models  # type: ignore # noqa: F401
from app.api.debug import router as debug_router
from app.api.health import router as health_router
from app.api.simulations import router as simulations_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(simulations_router)
app.include_router(debug_router)
