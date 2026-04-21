from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.relations.simulation_territory import SimulationTerritoryRelation
    from app.models.relations.territory_agent import TerritoryAgentRelation
    from app.models.territory.edge import TerritoryEdge


class Territory(Base):
    __tablename__ = "territories"

    __table_args__ = (
        CheckConstraint("food >= 0", name="ck_territories_food_non_negative"),
        CheckConstraint("food_capacity >= 0", name="ck_territories_food_capacity_non_negative"),
        CheckConstraint(
            "food_regen_per_tick >= 0",
            name="ck_territories_food_regen_per_tick_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    food: Mapped[float] = mapped_column(Float, default=0.0)
    temperature: Mapped[float] = mapped_column(Float, default=20.0)
    food_regen_per_tick: Mapped[float] = mapped_column(Float, default=1.0)
    food_capacity: Mapped[float] = mapped_column(Float, default=100.0)
    x: Mapped[float] = mapped_column(Float, default=0.0)
    y: Mapped[float] = mapped_column(Float, default=0.0)

    simulation_links: Mapped[list["SimulationTerritoryRelation"]] = relationship(
        back_populates="territory",
        cascade="all, delete-orphan",
    )
    agent_links: Mapped[list["TerritoryAgentRelation"]] = relationship(
        back_populates="territory",
        cascade="all, delete-orphan",
    )
    outgoing_edges: Mapped[list["TerritoryEdge"]] = relationship(
        foreign_keys="TerritoryEdge.source_id",
        back_populates="source_territory",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list["TerritoryEdge"]] = relationship(
        foreign_keys="TerritoryEdge.target_id",
        back_populates="target_territory",
        cascade="all, delete-orphan",
    )

    @property
    def position(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}

    @property
    def simulation_id(self) -> Optional[int]:
        return self.simulation_links[0].simulation_id if self.simulation_links else None
