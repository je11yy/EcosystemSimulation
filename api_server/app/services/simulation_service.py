from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.simulation import Simulation
from app.models.territory import Territory
from app.models.territory_edge import TerritoryEdge
from app.repositories.simulation_repository import SimulationRepository
from app.schemas.agent import AgentCreate
from app.schemas.territory import TerritoryCreate, TerritoryUpdate
from app.schemas.territory_edge import TerritoryEdgeCreate
from app.services.default_genome_factory import DefaultGenomeFactory
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

        agent = Agent(
            simulation_id=simulation_id,
            territory_id=payload.territory_id,
            hunger=payload.hunger,
            hp=payload.hp,
            base_strength=payload.base_strength,
            base_defense=payload.base_defense,
            sex=payload.sex,
            pregnant=payload.pregnant,
            ticks_to_birth=payload.ticks_to_birth,
            father_id=payload.father_id,
            base_temp_pref=payload.base_temp_pref,
            satisfaction=payload.satisfaction,
            alive=payload.alive,
        )
        self.db.add(agent)
        await self.db.flush()

        genome_factory = DefaultGenomeFactory()
        genes, gene_edges, gene_states = genome_factory.build_for_agent(agent.id)

        self.db.add_all(genes)
        self.db.add_all(gene_edges)
        self.db.add_all(gene_states)

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
