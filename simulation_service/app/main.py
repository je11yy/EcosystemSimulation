from fastapi import FastAPI

from app.api.runtime import router as runtime_router

app = FastAPI(title="EcoSim Simulation Service")

app.include_router(runtime_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
