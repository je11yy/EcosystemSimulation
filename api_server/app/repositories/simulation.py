from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Simulation, Territory, TerritoryEdge
from app.models.relations.simulation_territory import SimulationTerritoryRelation
from app.models.relations.simulation_user import SimulationUserRelation
from app.repositories.base import Repository


class SimulationRepository(Repository):
    async def list_by_user(self, user_id: int) -> list[tuple[Simulation, int]]:
        stmt = (
            select(Simulation, SimulationUserRelation.user_id)
            .join(SimulationUserRelation, SimulationUserRelation.simulation_id == Simulation.id)
            .where(SimulationUserRelation.user_id == user_id)
            .order_by(Simulation.updated_at.desc(), Simulation.id.desc())
            .options(selectinload(Simulation.user_links))
        )
        return list((await self.session.execute(stmt)).all())

    async def get_with_logs(self, simulation_id: int) -> Simulation | None:
        stmt = (
            select(Simulation)
            .where(Simulation.id == simulation_id)
            .options(
                selectinload(Simulation.user_links),
                selectinload(Simulation.logs),
            )
        )
        return await self.session.scalar(stmt)

    async def get_owned(self, simulation_id: int, user_id: int) -> Simulation | None:
        stmt = (
            select(Simulation)
            .join(
                SimulationUserRelation,
                SimulationUserRelation.simulation_id == Simulation.id,
            )
            .where(
                Simulation.id == simulation_id,
                SimulationUserRelation.user_id == user_id,
            )
            .options(
                selectinload(Simulation.user_links),
                selectinload(Simulation.logs),
            )
        )
        return await self.session.scalar(stmt)

    async def get_details_parts(
        self,
        simulation_id: int,
        user_id: int,
    ) -> tuple[Simulation | None, list[Territory], list[TerritoryEdge]]:
        simulation = await self.get_owned(simulation_id, user_id)
        if simulation is None:
            return None, [], []

        territories_stmt = (
            select(Territory)
            .join(
                SimulationTerritoryRelation,
                SimulationTerritoryRelation.territory_id == Territory.id,
            )
            .where(SimulationTerritoryRelation.simulation_id == simulation_id)
            .options(selectinload(Territory.simulation_links))
            .order_by(Territory.id)
        )
        territories = list((await self.session.scalars(territories_stmt)).all())
        territory_ids = {territory.id for territory in territories}

        edges: list[TerritoryEdge] = []
        if territory_ids:
            edges_stmt = (
                select(TerritoryEdge)
                .where(
                    TerritoryEdge.source_id.in_(territory_ids),
                    TerritoryEdge.target_id.in_(territory_ids),
                )
                .order_by(TerritoryEdge.id)
            )
            edges = list((await self.session.scalars(edges_stmt)).all())

        return simulation, territories, edges
