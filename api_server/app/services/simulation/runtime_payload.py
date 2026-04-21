from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.agent import AgentRepository
from app.repositories.genome.genome import GenomeRepository
from app.repositories.simulation import SimulationRepository
from app.services.simulation.runtime_snapshot import build_runtime_payload


class RuntimePayloadBuilder:
    def __init__(self, session: AsyncSession):
        self.simulations = SimulationRepository(session)
        self.agents = AgentRepository(session)
        self.genomes = GenomeRepository(session)

    async def build(self, user_id: int, simulation_id: int):
        simulation, territories, territory_edges = await self.simulations.get_details_parts(
            simulation_id,
            user_id,
        )
        if simulation is None:
            return None, None

        agents = await self.agents.list_by_simulation(simulation_id)
        genome_ids = {agent.genome_id for agent in agents if agent.genome_id is not None}
        genomes = []
        for genome_id in genome_ids:
            genome = await self.genomes.get_with_graph(genome_id)
            if genome is not None:
                genomes.append(genome)

        return (
            simulation,
            build_runtime_payload(
                simulation=simulation,
                territories=territories,
                territory_edges=territory_edges,
                agents=agents,
                genomes=genomes,
            ),
        )
