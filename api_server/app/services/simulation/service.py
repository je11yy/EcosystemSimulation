from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import SimulationStatus
from app.mappers.simulation import simulation_details_to_dict, simulation_to_dict
from app.models import Simulation, SimulationLog
from app.models.relations.simulation_user import SimulationUserRelation
from app.repositories.simulation import SimulationRepository
from app.schemas import SimulationCreate


class SimulationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.simulations = SimulationRepository(session)

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

    async def step(self, user_id: int, simulation_id: int) -> None:
        simulation = await self._get_owned(user_id, simulation_id)
        next_tick = simulation.tick + 1
        simulation.tick = next_tick
        self.session.add(
            SimulationLog(
                simulation_id=simulation_id,
                tick=next_tick,
                agent_decisions=[],
                step_result={
                    "eat": 0,
                    "move": 0,
                    "mate": 0,
                    "rest": 0,
                    "hunt": 0,
                    "deaths": 0,
                    "births": 0,
                    "fights": 0,
                },
                metrics={
                    "alive_population": 0,
                    "avg_hunger": 0.0,
                    "occupancy_by_territory": {},
                    "deaths_by_reason": {},
                    "successful_hunts": 0,
                    "unsuccessful_hunts": 0,
                    "consumed_food": 0,
                },
            )
        )
        await self.session.commit()

    async def _get_owned(self, user_id: int, simulation_id: int) -> Simulation:
        simulation = await self.simulations.get_owned(simulation_id, user_id)
        if simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")
        return simulation
