from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.config import settings
from app.schemas.simulation.init import BuildSimulationRequest
from app.schemas.simulation.start import StartSimulationRequest
from app.schemas.simulation.state import RuntimeSnapshot, RuntimeStatusResponse
from app.schemas.simulation.step import RuntimeStepResponse
from app.services.engine_factory import EngineFactory


@dataclass
class SimulationRuntime:
    simulation_id: int
    engine: Any
    status: str = "built"
    task: asyncio.Task | None = None
    last_result: dict[str, Any] | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @property
    def is_running(self) -> bool:
        return self.task is not None and not self.task.done()


class RuntimeManager:
    def __init__(self, engine_factory: EngineFactory | None = None):
        self.engine_factory = engine_factory or EngineFactory()
        self.runtimes: dict[int, SimulationRuntime] = {}

    async def build(self, payload: BuildSimulationRequest) -> RuntimeStatusResponse:
        await self.stop(payload.simulation_id, missing_ok=True)
        engine = self.engine_factory.build(payload)
        runtime = SimulationRuntime(simulation_id=payload.simulation_id, engine=engine)
        self.runtimes[payload.simulation_id] = runtime
        return self.status(payload.simulation_id, include_snapshot=True)

    async def step(self, simulation_id: int) -> RuntimeStepResponse:
        runtime = self._get_runtime(simulation_id)
        async with runtime.lock:
            result = runtime.engine.step()
            runtime.last_result = self._encode_step_result(result)
            snapshot = self._snapshot(runtime)
            return RuntimeStepResponse(
                simulation_id=simulation_id,
                tick=result.tick,
                result=runtime.last_result,
                snapshot=snapshot,
            )

    async def start(
        self,
        simulation_id: int,
        payload: StartSimulationRequest,
    ) -> RuntimeStatusResponse:
        runtime = self._get_runtime(simulation_id)
        if runtime.is_running:
            return self.status(simulation_id, include_snapshot=True)

        interval = payload.interval_seconds
        if interval is None:
            interval = settings.runtime_step_interval_seconds

        runtime.status = "running"
        runtime.task = asyncio.create_task(
            self._run_loop(
                runtime,
                interval_seconds=interval,
                max_steps=payload.max_steps,
            )
        )
        return self.status(simulation_id, include_snapshot=True)

    async def pause(self, simulation_id: int) -> RuntimeStatusResponse:
        runtime = self._get_runtime(simulation_id)
        await self._cancel_task(runtime)
        runtime.status = "paused"
        return self.status(simulation_id, include_snapshot=True)

    async def stop(
        self,
        simulation_id: int,
        missing_ok: bool = False,
    ) -> bool:
        runtime = self.runtimes.get(simulation_id)
        if runtime is None:
            if missing_ok:
                return False
            raise HTTPException(status_code=404, detail="Simulation runtime is not built")

        await self._cancel_task(runtime)
        runtime.status = "stopped"
        del self.runtimes[simulation_id]
        return True

    def status(
        self,
        simulation_id: int,
        include_snapshot: bool = False,
    ) -> RuntimeStatusResponse:
        runtime = self.runtimes.get(simulation_id)
        if runtime is None:
            return RuntimeStatusResponse(
                simulation_id=simulation_id,
                status="stopped",
                tick=0,
                is_built=False,
                is_running=False,
                snapshot=None,
            )

        return RuntimeStatusResponse(
            simulation_id=simulation_id,
            status=runtime.status,
            tick=runtime.engine.tick,
            is_built=True,
            is_running=runtime.is_running,
            snapshot=self._snapshot(runtime) if include_snapshot else None,
        )

    async def _run_loop(
        self,
        runtime: SimulationRuntime,
        interval_seconds: float,
        max_steps: int | None,
    ) -> None:
        completed_steps = 0
        try:
            while max_steps is None or completed_steps < max_steps:
                async with runtime.lock:
                    result = runtime.engine.step()
                    runtime.last_result = self._encode_step_result(result)
                completed_steps += 1
                await asyncio.sleep(max(0.0, interval_seconds))
        except asyncio.CancelledError:
            raise
        finally:
            if runtime.status == "running":
                runtime.status = "paused"

    async def _cancel_task(self, runtime: SimulationRuntime) -> None:
        if runtime.task is None or runtime.task.done():
            runtime.task = None
            return

        runtime.task.cancel()
        try:
            await runtime.task
        except asyncio.CancelledError:
            pass
        runtime.task = None

    def _get_runtime(self, simulation_id: int) -> SimulationRuntime:
        runtime = self.runtimes.get(simulation_id)
        if runtime is None:
            raise HTTPException(status_code=404, detail="Simulation runtime is not built")
        return runtime

    def _snapshot(self, runtime: SimulationRuntime) -> RuntimeSnapshot:
        engine = runtime.engine
        return RuntimeSnapshot(
            simulation_id=runtime.simulation_id,
            tick=engine.tick,
            status=runtime.status,
            agents=[self._agent_snapshot(agent) for agent in engine.agents.all()],
            territories=[
                jsonable_encoder(territory) for territory in engine.world.all_territories()
            ],
            last_result=runtime.last_result,
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
        }


runtime_manager = RuntimeManager()
