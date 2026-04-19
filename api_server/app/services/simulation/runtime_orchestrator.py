from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import SimulationStatus
from app.models import Simulation
from app.repositories.simulation import SimulationRepository
from app.services.simulation.runtime_client import SimulationRuntimeClient
from app.services.simulation.runtime_payload import RuntimePayloadBuilder
from app.services.simulation.runtime_persister import RuntimeSnapshotPersister


class SimulationRuntimeOrchestrator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.simulations = SimulationRepository(session)
        self.runtime = SimulationRuntimeClient()
        self.payload_builder = RuntimePayloadBuilder(session)
        self.persister = RuntimeSnapshotPersister(session)

    async def build_runtime(self, user_id: int, simulation_id: int) -> None:
        simulation, payload = await self._build_payload_or_404(user_id, simulation_id)
        await self.runtime.build(payload)
        simulation.status = SimulationStatus.LOADED.value
        await self.session.commit()

    async def start(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        state = await self._runtime_state_or_none(simulation_id)
        if state is not None and state.get("is_built"):
            await self.runtime.start(simulation_id)
        else:
            simulation, payload = await self._build_payload_or_404(user_id, simulation_id)
            await self.runtime.build(payload)
            await self.runtime.start(simulation_id)
        simulation.status = SimulationStatus.RUNNING.value
        await self.session.commit()

    async def pause(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        try:
            state = await self.runtime.state(simulation_id)
            if state.get("is_built"):
                await self.runtime.pause(simulation_id)
                await self._sync_runtime_state(user_id, simulation_id, simulation)
        except HTTPException:
            pass
        simulation.status = SimulationStatus.PAUSED.value
        await self.session.commit()

    async def stop(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        try:
            state = await self.runtime.state(simulation_id)
            if state.get("is_built"):
                await self.runtime.pause(simulation_id)
                await self._sync_runtime_state(user_id, simulation_id, simulation)
                await self.runtime.stop(simulation_id)
        except HTTPException:
            pass
        simulation.status = SimulationStatus.STOPPED.value
        await self.session.commit()

    async def step(self, user_id: int, simulation_id: int) -> None:
        simulation, payload = await self._build_payload_or_404(user_id, simulation_id)
        state = await self.runtime.state(simulation_id)
        if not state.get("is_built"):
            await self.runtime.build(payload)

        response = await self.runtime.step(simulation_id)
        result = response["result"]
        snapshot = response["snapshot"]

        simulation.tick = snapshot["tick"]
        await self.persister.save_result(simulation_id, result)
        await self.persister.apply_snapshot(user_id, snapshot, result)
        await self.session.commit()

    async def sync_runtime(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        await self._sync_runtime_state(user_id, simulation_id, simulation)
        await self.session.commit()

    async def stop_if_built(self, simulation_id: int) -> None:
        try:
            state = await self.runtime.state(simulation_id)
        except HTTPException:
            return
        if state.get("is_built"):
            await self.runtime.stop(simulation_id)

    async def mark_runtime_stale(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        state = await self._runtime_state_or_none(simulation_id)
        if state is not None and state.get("is_built"):
            if state.get("is_running"):
                await self.runtime.pause(simulation_id)
            await self._sync_runtime_state(user_id, simulation_id, simulation)
            await self.runtime.stop(simulation_id)
        simulation.status = SimulationStatus.DRAFT.value

    async def _sync_runtime_state(
        self,
        user_id: int,
        simulation_id: int,
        simulation: Simulation,
    ) -> None:
        state = await self._runtime_state_or_none(simulation_id)
        if state is None or not state.get("is_built"):
            return

        drained = await self.runtime.drain(simulation_id)
        snapshot = drained.get("snapshot")
        if snapshot is None:
            return

        results = drained.get("results", [])
        for result in results:
            await self.persister.save_result(simulation_id, result)

        simulation.tick = snapshot["tick"]
        combined_result = {
            "births": [birth for result in results for birth in result.get("births", [])]
        }
        await self.persister.apply_snapshot(user_id, snapshot, combined_result)

    async def _build_payload_or_404(self, user_id: int, simulation_id: int):
        simulation, payload = await self.payload_builder.build(user_id, simulation_id)
        if simulation is None or payload is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation, payload

    async def _runtime_state_or_none(self, simulation_id: int) -> dict | None:
        try:
            return await self.runtime.state(simulation_id)
        except HTTPException:
            return None

    async def _get_owned(self, user_id: int, simulation_id: int) -> Simulation:
        simulation = await self.simulations.get_owned(simulation_id, user_id)
        if simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation
