from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Territory
from app.models.relations.simulation_territory import SimulationTerritoryRelation
from app.repositories.base import Repository


class TerritoryRepository(Repository):
    async def list_by_simulation(self, simulation_id: int) -> list[Territory]:
        stmt = (
            select(Territory)
            .join(
                SimulationTerritoryRelation,
                SimulationTerritoryRelation.territory_id == Territory.id,
            )
            .where(SimulationTerritoryRelation.simulation_id == simulation_id)
            .options(selectinload(Territory.simulation_links))
            .order_by(Territory.id)
        )
        return list((await self.session.scalars(stmt)).all())

    async def simulation_id_for_territory(self, territory_id: int) -> int | None:
        link = await self.session.scalar(
            select(SimulationTerritoryRelation).where(
                SimulationTerritoryRelation.territory_id == territory_id
            )
        )
        return link.simulation_id if link else None
