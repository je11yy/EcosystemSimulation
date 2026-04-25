from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder

from app.schemas.simulation.batch import (
    RunBatchSimulationRequest,
    RunBatchSimulationResponse,
    RuntimeTickResult,
)
from app.schemas.simulation.state import RuntimeSnapshot
from app.services.engine_factory import EngineFactory


class RuntimeManager:
    def __init__(self, engine_factory: EngineFactory | None = None):
        self.engine_factory = engine_factory or EngineFactory()

    async def run_batch(self, payload: RunBatchSimulationRequest) -> RunBatchSimulationResponse:
        engine = self.engine_factory.build(payload.build)
        tick_results: list[RuntimeTickResult] = []

        for _ in range(payload.steps):
            result = engine.step()
            encoded_result = self._encode_step_result(result)
            tick_results.append(
                RuntimeTickResult(
                    result=encoded_result,
                    snapshot=self._snapshot(
                        simulation_id=payload.build.simulation_id,
                        status="stopped",
                        engine=engine,
                        last_result=encoded_result,
                    ),
                )
            )

        return RunBatchSimulationResponse(
            simulation_id=payload.build.simulation_id,
            steps=payload.steps,
            tick_results=tick_results,
            final_snapshot=self._snapshot(
                simulation_id=payload.build.simulation_id,
                status="stopped",
                engine=engine,
                last_result=tick_results[-1].result if tick_results else None,
            ),
        )

    def _snapshot(
        self,
        simulation_id: int,
        status: str,
        engine: Any,
        last_result: dict[str, Any] | None,
    ) -> RuntimeSnapshot:
        return RuntimeSnapshot(
            simulation_id=simulation_id,
            tick=engine.tick,
            status=status,
            agents=[self._agent_snapshot(agent) for agent in engine.agents.all()],
            territories=[
                jsonable_encoder(territory) for territory in engine.world.all_territories()
            ],
            last_result=last_result,
        )

    def _encode_step_result(self, result) -> dict[str, Any]:
        encoded = jsonable_encoder(result)
        encoded["step"] = jsonable_encoder(result.step)
        return encoded

    def _agent_snapshot(self, agent) -> dict[str, Any]:
        return {
            "id": agent.state.id,
            "sex": agent.state.sex.value,
            "territory_id": agent.state.location,
            "hunger": agent.state.hunger,
            "hp": agent.state.hp,
            "strength": agent.state.base_strength,
            "effective_strength": agent.state.effective_strength,
            "defense": agent.state.base_defense,
            "effective_defense": agent.state.effective_defense,
            "temp_pref": agent.state.base_temp_pref,
            "satisfaction": agent.state.satisfaction,
            "pregnant": agent.state.is_pregnant,
            "ticks_to_birth": agent.state.ticks_to_birth,
            "hunt_cooldown": agent.state.hunt_cooldown,
            "is_alive": agent.state.is_alive,
            "max_hp": agent.state.max_hp,
            "genome": self._genome_snapshot(agent.genome),
        }

    def _genome_snapshot(self, genome) -> dict[str, Any]:
        return {
            "genes": [
                {
                    "id": gene.id,
                    "effect_type": gene.effect_type.value,
                    "x": gene.x,
                    "y": gene.y,
                    "threshold": gene.threshold,
                    "weight": gene.weight,
                    "default_active": gene.default_active,
                }
                for gene in genome.genes.values()
            ],
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "weight": edge.weight,
                }
                for edge in genome.graph.edges.values()
            ],
        }


runtime_manager = RuntimeManager()
