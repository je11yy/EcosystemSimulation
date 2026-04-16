from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Agent
from app.models.relations.simulation_agent import SimulationAgentRelation
from app.models.relations.simulation_territory import SimulationTerritoryRelation
from app.repositories.base import Repository


class AgentRepository(Repository):
    async def get_with_links(self, agent_id: int) -> Agent | None:
        stmt = (
            select(Agent)
            .where(Agent.id == agent_id)
            .options(
                selectinload(Agent.territory_links),
                selectinload(Agent.genome_links),
                selectinload(Agent.simulation_links),
            )
        )
        return await self.session.scalar(stmt)

    async def list_by_simulation(self, simulation_id: int) -> list[Agent]:
        stmt = (
            select(Agent)
            .join(SimulationAgentRelation, SimulationAgentRelation.agent_id == Agent.id)
            .where(SimulationAgentRelation.simulation_id == simulation_id)
            .options(
                selectinload(Agent.territory_links),
                selectinload(Agent.genome_links),
            )
            .order_by(Agent.id)
        )
        return list((await self.session.scalars(stmt)).all())

    async def simulation_id_for_territory(self, territory_id: int) -> int | None:
        link = await self.session.scalar(
            select(SimulationTerritoryRelation).where(
                SimulationTerritoryRelation.territory_id == territory_id
            )
        )
        return link.simulation_id if link else None
