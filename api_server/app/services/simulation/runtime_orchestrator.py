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

    async def run_batch(self, user_id: int, simulation_id: int, steps: int) -> None:
        simulation, payload = await self._build_payload_or_404(user_id, simulation_id)
        response = await self.runtime.run_batch(payload, steps)
        tick_results = response.get("tick_results", [])
        final_snapshot = response["final_snapshot"]

        all_births: list[dict] = []
        for tick_result in tick_results:
            result = tick_result["result"]
            snapshot = tick_result["snapshot"]
            all_births.extend(result.get("births", []))
            await self.persister.save_result(simulation_id, result, snapshot)

        simulation.tick = final_snapshot["tick"]
        simulation.status = SimulationStatus.STOPPED.value
        await self.persister.apply_snapshot(
            user_id,
            final_snapshot,
            {"births": all_births},
        )
        await self.session.commit()

    async def stop_if_built(self, simulation_id: int) -> None:
        return None

    async def mark_runtime_stale(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        simulation.status = SimulationStatus.DRAFT.value

    async def _build_payload_or_404(self, user_id: int, simulation_id: int):
        simulation, payload = await self.payload_builder.build(user_id, simulation_id)
        if simulation is None or payload is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation, payload

    async def _get_owned(self, user_id: int, simulation_id: int) -> Simulation:
        simulation = await self.simulations.get_owned(simulation_id, user_id)
        if simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation
