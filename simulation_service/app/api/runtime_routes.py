from fastapi import APIRouter, HTTPException

from app.schemas.runtime import (
    RuntimeDeleteResponseDTO,
    RuntimeStartResponseDTO,
    RuntimeStateResponseDTO,
    RuntimeStepResponseDTO,
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

    @router.post("/{simulation_id}/step", response_model=RuntimeStepResponseDTO)
    async def step_runtime(simulation_id: str):  # type: ignore
        if not runtime_manager.has(simulation_id):
            raise HTTPException(status_code=404, detail="Runtime not found")

        handle = runtime_manager.get(simulation_id)

        async with handle.lock:
            step_result = handle.engine.step()
            state = handle.engine.get_state()

        return RuntimeStepResponseDTO(
            ok=True,
            simulation_id=simulation_id,
            state=state.to_dict(),
            step_result={
                "tick": int(step_result.tick),
                "decisions": [
                    {
                        "tick": int(decision.tick),
                        "agent_id": decision.agent_id,
                        "chosen": {
                            "type": decision.chosen.type.value,
                            "to_territory": decision.chosen.to_territory,
                            "partner_id": decision.chosen.partner_id,
                            "tag": decision.chosen.tag,
                        },
                    }
                    for decision in step_result.decisions
                ],
                "applied_results": [
                    {
                        "agent_id": result.agent_id,
                        "action_type": result.action_type,
                        "success": result.success,
                        "reason": result.reason,
                        "consumed_food": result.consumed_food,
                        "created_pregnancy": result.created_pregnancy,
                        "hp_loss": result.hp_loss,
                    }
                    for result in step_result.applied_results
                ],
                "deaths": [
                    {
                        "agent_id": death.agent_id,
                        "reason": death.reason,
                        "tick": int(death.tick),
                    }
                    for death in step_result.deaths
                ],
                "births": [
                    {
                        "parent_id": birth.parent_id,
                        "child_id": birth.child_id,
                        "tick": int(birth.tick),
                    }
                    for birth in step_result.births
                ],
                "fights": [
                    {
                        "territory_id": fight.territory_id,
                        "winner_id": fight.winner_id,
                        "loser_id": fight.loser_id,
                        "loser_hp_loss": fight.loser_hp_loss,
                    }
                    for fight in step_result.fights
                ],
            },
        )

    return router
