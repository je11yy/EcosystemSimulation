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
                            "target_id": decision.chosen.target_id,
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
                        "hunger_restored": result.hunger_restored,
                        "target_id": result.target_id,
                        "damage_to_target": result.damage_to_target,
                        "target_died": result.target_died,
                        "hunter_died": result.hunter_died,
                        "hunger_delta": result.hunger_delta,
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
                "hunts": [
                    {
                        "territory_id": hunt.territory_id,
                        "hunter_id": hunt.hunter_id,
                        "target_id": hunt.target_id,
                        "success": hunt.success,
                        "damage_to_target": hunt.damage_to_target,
                        "damage_to_hunter": hunt.damage_to_hunter,
                        "target_died": hunt.target_died,
                        "hunter_died": hunt.hunter_died,
                        "hunger_restored": hunt.hunger_restored,
                    }
                    for hunt in step_result.hunts
                ],
                "metrics": {
                    "alive_population": step_result.metrics.alive_population,
                    "population_by_species_group": step_result.metrics.population_by_species_group,
                    "avg_hunger_alive": step_result.metrics.avg_hunger_alive,
                    "avg_hp_alive": step_result.metrics.avg_hp_alive,
                    "avg_hunt_cooldown_alive": step_result.metrics.avg_hunt_cooldown_alive,
                    "occupancy_by_territory": step_result.metrics.occupancy_by_territory,
                    "action_counts": step_result.metrics.action_counts,
                    "successful_hunts": step_result.metrics.successful_hunts,
                    "births_count": step_result.metrics.births_count,
                    "deaths_count": step_result.metrics.deaths_count,
                    "deaths_by_reason": step_result.metrics.deaths_by_reason,
                },
                "metrics_history": [
                    {
                        "tick": point.tick,
                        "alive_population": point.alive_population,
                        "avg_hunger_alive": point.avg_hunger_alive,
                        "avg_hp_alive": point.avg_hp_alive,
                        "avg_hunt_cooldown_alive": point.avg_hunt_cooldown_alive,
                        "successful_hunts": point.successful_hunts,
                        "births_count": point.births_count,
                        "deaths_count": point.deaths_count,
                        "population_by_species_group": point.population_by_species_group,
                        "occupancy_by_territory": point.occupancy_by_territory,
                        "action_counts": point.action_counts,
                        "deaths_by_reason": point.deaths_by_reason,
                    }
                    for point in step_result.metrics_history
                ],
            },
        )

    return router
