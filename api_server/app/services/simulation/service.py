from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import SimulationStatus
from app.mappers.simulation import simulation_details_to_dict, simulation_to_dict
from app.models import Simulation
from app.models.relations.simulation_user import SimulationUserRelation
from app.repositories.simulation import SimulationRepository
from app.schemas import SimulationBatchRunRequest, SimulationCreate
from app.services.simulation.runtime_orchestrator import SimulationRuntimeOrchestrator


class SimulationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.simulations = SimulationRepository(session)
        self.runtime_orchestrator = SimulationRuntimeOrchestrator(session)

    async def list_by_user(self, user_id: int) -> list[dict]:
        rows = await self.simulations.list_by_user(user_id)
        return [simulation_to_dict(simulation, owner_id) for simulation, owner_id in rows]

    async def create(self, user_id: int, payload: SimulationCreate) -> None:
        simulation = Simulation(name=payload.name)
        self.session.add(simulation)
        await self.session.flush()
        self.session.add(SimulationUserRelation(user_id=user_id, simulation_id=simulation.id))
        await self.session.commit()

    async def get_details(self, user_id: int, simulation_id: int) -> dict:
        simulation, territories, edges = await self.simulations.get_details_parts(
            simulation_id,
            user_id,
        )
        if simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation_details_to_dict(simulation, territories, edges)

    async def delete(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        await self.runtime_orchestrator.stop_if_built(simulation_id)
        await self.session.delete(simulation)
        await self.session.commit()

    async def rename(self, user_id: int, simulation_id: int, name: str) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        simulation.name = name
        await self.session.commit()

    async def set_status(self, user_id: int, simulation_id: int, status: SimulationStatus) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        simulation.status = status.value
        await self.session.commit()

    async def run_batch(
        self,
        user_id: int,
        simulation_id: int,
        payload: SimulationBatchRunRequest,
    ) -> None:
        await self.runtime_orchestrator.run_batch(user_id, simulation_id, payload.steps)

    async def _get_owned(self, user_id: int, simulation_id: int) -> Simulation:
        simulation = await self.simulations.get_owned(simulation_id, user_id)
        if simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation
