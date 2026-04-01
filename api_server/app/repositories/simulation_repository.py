from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import Agent
from app.models.simulation import Simulation


class SimulationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, user_id: int, name: str) -> Simulation:
        simulation = Simulation(
            user_id=user_id,
            name=name,
            status="draft",
            tick=0,
        )
        self.db.add(simulation)
        await self.db.commit()
        await self.db.refresh(simulation)
        return simulation

    async def get_by_id(self, simulation_id: int) -> Optional[Simulation]:
        stmt = select(Simulation).where(Simulation.id == simulation_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_full_by_id(self, simulation_id: int) -> Optional[Simulation]:
        stmt = (
            select(Simulation)
            .where(Simulation.id == simulation_id)
            .options(
                selectinload(Simulation.territories),
                selectinload(Simulation.territory_edges),
                selectinload(Simulation.agents).selectinload(Agent.genes),
                selectinload(Simulation.agents).selectinload(Agent.gene_edges),
                selectinload(Simulation.agents).selectinload(Agent.gene_states),
                selectinload(Simulation.metrics_history),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: int) -> list[Simulation]:
        stmt = (
            select(Simulation).where(Simulation.user_id == user_id).order_by(Simulation.id.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
