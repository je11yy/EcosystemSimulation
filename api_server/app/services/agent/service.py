from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.mappers.agent import agent_to_dict
from app.models import Agent, Genome, Territory
from app.models.relations.genome_agent import GenomeAgentRelation
from app.models.relations.simulation_agent import SimulationAgentRelation
from app.models.relations.territory_agent import TerritoryAgentRelation
from app.repositories.agent import AgentRepository
from app.schemas import AgentCreate
from app.services.errors import get_or_404


class AgentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session)

    async def list_by_simulation(self, simulation_id: int) -> list[dict]:
        agents = await self.agents.list_by_simulation(simulation_id)
        return [agent_to_dict(agent) for agent in agents]

    async def create(self, payload: AgentCreate) -> None:
        await get_or_404(self.session, Territory, payload.territory_id, "Territory")
        if payload.genome_id is not None:
            await get_or_404(self.session, Genome, payload.genome_id, "Genome")

        simulation_id = await self.agents.simulation_id_for_territory(payload.territory_id)
        if simulation_id is None:
            raise HTTPException(status_code=400, detail="Territory is not linked to a simulation")

        agent = Agent(sex=payload.sex.value)
        self.session.add(agent)
        await self.session.flush()
        self.session.add(
            TerritoryAgentRelation(agent_id=agent.id, territory_id=payload.territory_id)
        )
        self.session.add(SimulationAgentRelation(agent_id=agent.id, simulation_id=simulation_id))
        if payload.genome_id is not None:
            self.session.add(GenomeAgentRelation(agent_id=agent.id, genome_id=payload.genome_id))
        await self.session.commit()

    async def delete(self, agent_id: int) -> None:
        agent = await get_or_404(self.session, Agent, agent_id, "Agent")
        await self.session.delete(agent)
        await self.session.commit()

    async def update(self, agent_id: int, payload: AgentCreate) -> None:
        agent = await self.agents.get_with_links(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")

        await get_or_404(self.session, Territory, payload.territory_id, "Territory")
        if payload.genome_id is not None:
            await get_or_404(self.session, Genome, payload.genome_id, "Genome")

        simulation_id = await self.agents.simulation_id_for_territory(payload.territory_id)
        if simulation_id is None:
            raise HTTPException(status_code=400, detail="Territory is not linked to a simulation")

        agent.sex = payload.sex.value

        await self.session.execute(
            delete(TerritoryAgentRelation).where(TerritoryAgentRelation.agent_id == agent_id)
        )
        self.session.add(
            TerritoryAgentRelation(agent_id=agent_id, territory_id=payload.territory_id)
        )

        await self.session.execute(
            delete(SimulationAgentRelation).where(SimulationAgentRelation.agent_id == agent_id)
        )
        self.session.add(SimulationAgentRelation(agent_id=agent_id, simulation_id=simulation_id))

        await self.session.execute(
            delete(GenomeAgentRelation).where(GenomeAgentRelation.agent_id == agent_id)
        )
        if payload.genome_id is not None:
            self.session.add(GenomeAgentRelation(agent_id=agent_id, genome_id=payload.genome_id))

        await self.session.commit()
