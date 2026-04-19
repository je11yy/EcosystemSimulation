from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.mappers.territory import territory_edge_to_dict, territory_to_dict
from app.models import Simulation, Territory, TerritoryEdge
from app.models.relations.simulation_territory import SimulationTerritoryRelation
from app.repositories.territory.edge import TerritoryEdgeRepository
from app.repositories.territory.territory import TerritoryRepository
from app.schemas import Position, TerritoryCreate, TerritoryEdgeCreate
from app.services.errors import get_or_404


class TerritoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.territories = TerritoryRepository(session)
        self.edges = TerritoryEdgeRepository(session)

    async def list_by_simulation(self, simulation_id: int) -> list[dict]:
        territories = await self.territories.list_by_simulation(simulation_id)
        return [territory_to_dict(territory) for territory in territories]

    async def create(self, payload: TerritoryCreate) -> None:
        if payload.simulation_id is None:
            raise HTTPException(status_code=400, detail="simulation_id is required")
        await get_or_404(self.session, Simulation, payload.simulation_id, "Simulation")

        territory = Territory(
            food=payload.food if payload.food is not None else payload.food_capacity,
            food_capacity=payload.food_capacity,
            food_regen_per_tick=payload.food_regen_per_tick,
            temperature=payload.temperature,
            x=payload.position.x,
            y=payload.position.y,
        )
        self.session.add(territory)
        await self.session.flush()
        self.session.add(
            SimulationTerritoryRelation(
                territory_id=territory.id,
                simulation_id=payload.simulation_id,
            )
        )
        await self.session.commit()

    async def delete(self, territory_id: int) -> None:
        territory = await get_or_404(self.session, Territory, territory_id, "Territory")
        agents = [link.agent for link in territory.agent_links]
        for agent in agents:
            await self.session.delete(agent)
        await self.session.delete(territory)
        await self.session.commit()

    async def update(self, territory_id: int, payload: TerritoryCreate) -> None:
        territory = await get_or_404(self.session, Territory, territory_id, "Territory")
        if payload.food is not None:
            territory.food = payload.food
        territory.food_capacity = payload.food_capacity
        territory.food_regen_per_tick = payload.food_regen_per_tick
        territory.temperature = payload.temperature
        territory.x = payload.position.x
        territory.y = payload.position.y
        if territory.food > territory.food_capacity:
            territory.food = territory.food_capacity
        await self.session.commit()

    async def update_position(self, territory_id: int, position: Position) -> None:
        territory = await get_or_404(self.session, Territory, territory_id, "Territory")
        territory.x = position.x
        territory.y = position.y
        await self.session.commit()

    async def list_edges_by_simulation(self, simulation_id: int) -> list[dict]:
        edges = await self.edges.list_by_simulation(simulation_id)
        return [territory_edge_to_dict(edge) for edge in edges]

    async def create_edge(self, payload: TerritoryEdgeCreate) -> None:
        await get_or_404(self.session, Territory, payload.source, "Source territory")
        await get_or_404(self.session, Territory, payload.target, "Target territory")

        source_simulation_id = await self.territories.simulation_id_for_territory(payload.source)
        target_simulation_id = await self.territories.simulation_id_for_territory(payload.target)
        if source_simulation_id != target_simulation_id:
            raise HTTPException(
                status_code=400,
                detail="Edge territories must belong to one simulation",
            )
        if payload.simulation_id is not None and payload.simulation_id != source_simulation_id:
            raise HTTPException(
                status_code=400,
                detail="simulation_id does not match edge territories",
            )

        self.session.add(
            TerritoryEdge(
                source_id=payload.source,
                target_id=payload.target,
                movement_cost=payload.weight,
            )
        )
        await self.session.commit()

    async def delete_edge(self, edge_id: int) -> None:
        edge = await get_or_404(self.session, TerritoryEdge, edge_id, "Territory edge")
        await self.session.delete(edge)
        await self.session.commit()

    async def update_edge_weight(self, edge_id: int, weight: float) -> None:
        edge = await get_or_404(self.session, TerritoryEdge, edge_id, "Territory edge")
        edge.weight = weight
        await self.session.commit()
