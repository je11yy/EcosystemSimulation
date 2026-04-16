from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.simulation import Simulation
    from app.models.territory.territory import Territory


class SimulationTerritoryRelation(Base):
    __tablename__ = "simulation_territory_relations"

    __table_args__ = (
        UniqueConstraint("territory_id", name="uq_simulation_territory_relations_territory"),
    )

    territory_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    territory: Mapped["Territory"] = relationship(back_populates="simulation_links")
    simulation: Mapped["Simulation"] = relationship(back_populates="territory_links")
