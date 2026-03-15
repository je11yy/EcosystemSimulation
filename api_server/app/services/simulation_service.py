from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.simulation_repository import SimulationRepository
from app.services.engine_mapper import EngineMapper


class SimulationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = SimulationRepository(db)
        self.mapper = EngineMapper()

    async def create_simulation(self, user_id: int, name: str):
        return await self.repo.create(user_id=user_id, name=name)

    async def get_simulation(self, simulation_id: int):
        return await self.repo.get_by_id(simulation_id)

    async def get_full_simulation(self, simulation_id: int):
        return await self.repo.get_full_by_id(simulation_id)

    async def list_user_simulations(self, user_id: int):
        return await self.repo.list_by_user_id(user_id=user_id)

    async def build_init_dto(self, simulation_id: int):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return None
        return self.mapper.to_init_dto(simulation)
