from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agents, auth, genomes, simulations, territories

app = FastAPI(title="Ecosystem Simulation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(simulations.router)
app.include_router(genomes.router)
app.include_router(agents.router)
app.include_router(territories.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
