from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.mappers.agent import agent_to_dict
from app.models import Agent, Territory
from app.models.relations.genome_agent import GenomeAgentRelation
from app.models.relations.simulation_agent import SimulationAgentRelation
from app.models.relations.territory_agent import TerritoryAgentRelation
from app.repositories.agent import AgentRepository
from app.repositories.genome.genome import GenomeRepository
from app.repositories.simulation import SimulationRepository
from app.schemas import AgentCreate
from app.services.errors import get_or_404
from app.services.simulation.runtime_orchestrator import SimulationRuntimeOrchestrator


class AgentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session)
        self.genomes = GenomeRepository(session)
        self.simulations = SimulationRepository(session)
        self.runtime_orchestrator = SimulationRuntimeOrchestrator(session)

    async def list_by_simulation(self, simulation_id: int, user_id: int) -> list[dict]:
        await self._ensure_simulation_owned(simulation_id, user_id)
        agents = await self.agents.list_by_simulation(simulation_id)
        return [agent_to_dict(agent) for agent in agents]

    async def create(self, payload: AgentCreate, user_id: int) -> None:
        await get_or_404(self.session, Territory, payload.territory_id, "Territory")
        if payload.genome_id is not None:
            await self._ensure_genome_available(payload.genome_id, user_id)

        simulation_id = await self.agents.simulation_id_for_territory(payload.territory_id)
        if simulation_id is None:
            raise HTTPException(status_code=400, detail="Territory is not linked to a simulation")
        await self._ensure_simulation_owned(simulation_id, user_id)
        await self.runtime_orchestrator.mark_runtime_stale(user_id, simulation_id)

        agent = Agent(sex=payload.sex.value, satisfaction=3.0, hp=5.0)
        self.session.add(agent)
        await self.session.flush()
        self.session.add(
            TerritoryAgentRelation(agent_id=agent.id, territory_id=payload.territory_id)
        )
        self.session.add(SimulationAgentRelation(agent_id=agent.id, simulation_id=simulation_id))
        if payload.genome_id is not None:
            self.session.add(GenomeAgentRelation(agent_id=agent.id, genome_id=payload.genome_id))
        await self.session.commit()

    async def delete(self, agent_id: int, user_id: int) -> None:
        simulation_id = await self._ensure_agent_owned(agent_id, user_id)
        await self.runtime_orchestrator.mark_runtime_stale(user_id, simulation_id)
        agent = await get_or_404(self.session, Agent, agent_id, "Agent")
        await self.session.delete(agent)
        await self.session.commit()

    async def update(self, agent_id: int, payload: AgentCreate, user_id: int) -> None:
        current_simulation_id = await self._ensure_agent_owned(agent_id, user_id)
        agent = await self.agents.get_with_links(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")

        await get_or_404(self.session, Territory, payload.territory_id, "Territory")
        if payload.genome_id is not None:
            await self._ensure_genome_available(payload.genome_id, user_id)

        simulation_id = await self.agents.simulation_id_for_territory(payload.territory_id)
        if simulation_id is None:
            raise HTTPException(status_code=400, detail="Territory is not linked to a simulation")
        await self._ensure_simulation_owned(simulation_id, user_id)
        await self.runtime_orchestrator.mark_runtime_stale(user_id, current_simulation_id)
        if simulation_id != current_simulation_id:
            await self.runtime_orchestrator.mark_runtime_stale(user_id, simulation_id)

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

    async def _ensure_agent_owned(self, agent_id: int, user_id: int) -> int:
        simulation_id = await self.agents.simulation_id_for_agent(agent_id)
        if simulation_id is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        await self._ensure_simulation_owned(simulation_id, user_id)
        return simulation_id

    async def _ensure_simulation_owned(self, simulation_id: int, user_id: int) -> None:
        simulation = await self.simulations.get_owned(simulation_id, user_id)
        if simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")

    async def _ensure_genome_available(self, genome_id: int, user_id: int) -> None:
        genome = await self.genomes.get_available_with_graph(genome_id, user_id)
        if genome is None:
            raise HTTPException(status_code=404, detail="Genome not found")
