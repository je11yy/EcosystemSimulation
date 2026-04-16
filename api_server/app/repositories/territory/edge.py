from sqlalchemy import select

from app.models import Territory, TerritoryEdge
from app.models.relations.simulation_territory import SimulationTerritoryRelation
from app.repositories.base import Repository


class TerritoryEdgeRepository(Repository):
    async def list_by_simulation(self, simulation_id: int) -> list[TerritoryEdge]:
        territory_ids = set(
            (
                await self.session.scalars(
                    select(Territory.id)
                    .join(
                        SimulationTerritoryRelation,
                        SimulationTerritoryRelation.territory_id == Territory.id,
                    )
                    .where(SimulationTerritoryRelation.simulation_id == simulation_id)
                )
            ).all()
        )
        if not territory_ids:
            return []

        edges = await self.session.scalars(
            select(TerritoryEdge)
            .where(
                TerritoryEdge.source_id.in_(territory_ids),
                TerritoryEdge.target_id.in_(territory_ids),
            )
            .order_by(TerritoryEdge.id)
        )
        return list(edges.all())
