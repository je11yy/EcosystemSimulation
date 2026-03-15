from fastapi import APIRouter, HTTPException

from app.schemas.runtime import (
    RuntimeDeleteResponseDTO,
    RuntimeStartResponseDTO,
    RuntimeStateResponseDTO,
    SimulationInitDTO,
)
from app.services.engine_factory import EngineFactory
from app.services.runtime_manager import RuntimeManager


def build_runtime_router(
    runtime_manager: RuntimeManager,
    engine_factory: EngineFactory,
) -> APIRouter:
    router = APIRouter(prefix="/runtime", tags=["runtime"])

    @router.post("/start", response_model=RuntimeStartResponseDTO)
    async def start_runtime(payload: SimulationInitDTO):  # type: ignore
        engine = engine_factory.build_from_init_dto(payload)
        runtime_manager.put(payload.simulation_id, engine)

        state = engine.get_state()

        return RuntimeStartResponseDTO(
            ok=True,
            simulation_id=payload.simulation_id,
            tick=state.tick,
            loaded_agents=len(state.agents),
            loaded_territories=len(state.territories),
        )

    @router.get("/{simulation_id}/state", response_model=RuntimeStateResponseDTO)
    async def get_runtime_state(simulation_id: str):  # type: ignore
        if not runtime_manager.has(simulation_id):
            raise HTTPException(status_code=404, detail="Runtime not found")

        handle = runtime_manager.get(simulation_id)
        state = handle.engine.get_state()

        return RuntimeStateResponseDTO(
            ok=True,
            simulation_id=simulation_id,
            state=state.to_dict(),
        )

    @router.delete("/{simulation_id}", response_model=RuntimeDeleteResponseDTO)
    async def delete_runtime(simulation_id: str):  # type: ignore
        removed = runtime_manager.delete(simulation_id)

        return RuntimeDeleteResponseDTO(
            ok=True,
            simulation_id=simulation_id,
            removed=removed,
        )

    return router
