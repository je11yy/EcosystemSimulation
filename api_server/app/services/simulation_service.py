import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.gene import Gene
from app.models.gene_edge import GeneEdge
from app.models.gene_state import GeneState
from app.models.genome_template import GenomeTemplate
from app.models.simulation import Simulation
from app.models.territory import Territory
from app.models.territory_edge import TerritoryEdge
from app.repositories.genome_template_repository import GenomeTemplateRepository
from app.repositories.simulation_repository import SimulationRepository
from app.schemas.agent import AgentCreate
from app.schemas.territory import TerritoryCreate, TerritoryUpdate
from app.schemas.territory_edge import TerritoryEdgeCreate
from app.services.engine_mapper import EngineMapper


class SimulationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = SimulationRepository(db)
        self.mapper = EngineMapper()
        self.db = db

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

    async def set_status(self, simulation: Simulation, status: str) -> None:
        simulation.status = status
        await self.db.commit()
        await self.db.refresh(simulation)

    async def create_territory(self, simulation_id: int, payload: TerritoryCreate):
        simulation = await self.repo.get_by_id(simulation_id)
        if simulation is None:
            return None

        territory = Territory(
            simulation_id=simulation_id,
            food=payload.food,
            temperature=payload.temperature,
            food_regen_per_tick=payload.food_regen_per_tick,
            food_capacity=payload.food_capacity,
            x=payload.x,
            y=payload.y,
        )
        self.db.add(territory)
        await self.db.commit()
        await self.db.refresh(territory)
        return territory

    async def create_agent(self, simulation_id: int, payload: AgentCreate):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return None, "simulation_not_found"

        territory_ids = {territory.id for territory in simulation.territories}
        if payload.territory_id not in territory_ids:
            return None, "territory_not_found"

        stmt = select(GenomeTemplate).where(GenomeTemplate.id == payload.genome_template_id)
        result = await self.db.execute(stmt)
        genome_template = result.scalar_one_or_none()

        if genome_template is None:
            return None, "genome_template_not_found"

        genome_template = await GenomeTemplateRepository(self.db).get_full_by_id(
            payload.genome_template_id
        )
        if genome_template is None:
            return None, "genome_template_not_found"

        agent = Agent(
            id=str(uuid.uuid4()),
            simulation_id=simulation_id,
            territory_id=payload.territory_id,
            hunger=payload.hunger,
            hp=payload.hp,
            base_strength=payload.base_strength,
            base_defense=payload.base_defense,
            sex=payload.sex,
            species_group=genome_template.species_group,
            pregnant=payload.pregnant,
            ticks_to_birth=payload.ticks_to_birth,
            hunt_cooldown=payload.hunt_cooldown,
            father_id=payload.father_id,
            base_temp_pref=payload.base_temp_pref,
            satisfaction=payload.satisfaction,
            alive=payload.alive,
        )
        self.db.add(agent)
        await self.db.flush()

        gene_id_map: dict[int, int] = {}
        effect_type_to_agent_gene_id: dict[str, int] = {}

        for template_gene in genome_template.genes:
            agent_gene = Gene(
                agent_id=agent.id,
                name=template_gene.name,
                effect_type=template_gene.effect_type,
                chromosome_id=template_gene.chromosome_id,
                position=template_gene.position,
                default_active=template_gene.default_active,
                threshold=template_gene.threshold,
            )

            self.db.add(agent_gene)
            await self.db.flush()

            gene_id_map[template_gene.id] = agent_gene.id
            effect_type_to_agent_gene_id[str(template_gene.effect_type)] = agent_gene.id

        for template_edge in genome_template.edges:
            source_gene_id = gene_id_map.get(template_edge.source_gene_id)
            target_gene_id = gene_id_map.get(template_edge.target_gene_id)

            if source_gene_id is None or target_gene_id is None:
                continue

            self.db.add(
                GeneEdge(
                    agent_id=agent.id,
                    source_gene_id=source_gene_id,
                    target_gene_id=target_gene_id,
                    weight=template_edge.weight,
                )
            )

        for template_state in genome_template.gene_states:
            mapped_gene_id = None

            if template_state.gene_id is not None:
                mapped_gene_id = gene_id_map.get(template_state.gene_id)

            if mapped_gene_id is None and hasattr(template_state, "effect_type"):
                effect_type = getattr(template_state, "effect_type", None)
                if effect_type is not None:
                    mapped_gene_id = effect_type_to_agent_gene_id.get(str(effect_type))

            if mapped_gene_id is None:
                continue

            self.db.add(
                GeneState(
                    agent_id=agent.id,
                    gene_id=str(mapped_gene_id),
                    is_active=template_state.is_active,
                )
            )

        await self.db.commit()
        await self.db.refresh(agent)
        return agent, None

    async def create_territory_edge(self, simulation_id: int, payload: TerritoryEdgeCreate):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return None, "simulation_not_found"

        territory_ids = {territory.id for territory in simulation.territories}

        if payload.source_territory_id not in territory_ids:
            return None, "source_not_found"

        if payload.target_territory_id not in territory_ids:
            return None, "target_not_found"

        if payload.source_territory_id == payload.target_territory_id:
            return None, "same_territory"

        # не даём создать дубликат ребра в обе стороны
        for edge in simulation.territory_edges:
            direct_match = (
                edge.source_territory_id == payload.source_territory_id
                and edge.target_territory_id == payload.target_territory_id
            )
            reverse_match = (
                edge.source_territory_id == payload.target_territory_id
                and edge.target_territory_id == payload.source_territory_id
            )
            if direct_match or reverse_match:
                return None, "edge_already_exists"

        edge = TerritoryEdge(
            simulation_id=simulation_id,
            source_territory_id=payload.source_territory_id,
            target_territory_id=payload.target_territory_id,
            movement_cost=payload.movement_cost,
        )
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)

        return edge, None

    async def update_territory(
        self, simulation_id: int, territory_id: int, payload: TerritoryUpdate
    ):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return None, "simulation_not_found"

        territory = next(
            (territory for territory in simulation.territories if territory.id == territory_id),
            None,
        )
        if territory is None:
            return None, "territory_not_found"

        if payload.food is not None:
            territory.food = payload.food
        if payload.temperature is not None:
            territory.temperature = payload.temperature
        if payload.food_regen_per_tick is not None:
            territory.food_regen_per_tick = payload.food_regen_per_tick
        if payload.food_capacity is not None:
            territory.food_capacity = payload.food_capacity

        territory.x = payload.x
        territory.y = payload.y

        await self.db.commit()
        await self.db.refresh(territory)
        return territory, None

    async def delete_territory(self, simulation_id: int, territory_id: int):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return "simulation_not_found"

        territory = next(
            (territory for territory in simulation.territories if territory.id == territory_id),
            None,
        )
        if territory is None:
            return "territory_not_found"

        await self.db.delete(territory)
        await self.db.commit()
        return None

    async def delete_territory_edge(self, simulation_id: int, edge_id: int):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return "simulation_not_found"

        edge = next(
            (edge for edge in simulation.territory_edges if edge.id == edge_id),
            None,
        )
        if edge is None:
            return "edge_not_found"

        await self.db.delete(edge)
        await self.db.commit()
        return None

    async def delete_agent(self, simulation_id: int, agent_id: int):
        simulation = await self.repo.get_full_by_id(simulation_id)
        if simulation is None:
            return "simulation_not_found"

        agent = next(
            (agent for agent in simulation.agents if agent.id == agent_id),
            None,
        )
        if agent is None:
            return "agent_not_found"

        await self.db.delete(agent)
        await self.db.commit()
        return None
