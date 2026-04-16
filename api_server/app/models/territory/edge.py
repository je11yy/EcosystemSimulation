from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.territory.territory import Territory


class TerritoryEdge(Base):
    __tablename__ = "territory_edges"

    __table_args__ = (
        CheckConstraint("movement_cost >= 0", name="ck_territory_edges_movement_cost_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        index=True,
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        index=True,
    )
    movement_cost: Mapped[float] = mapped_column(Float, default=1.0)

    source_territory: Mapped["Territory"] = relationship(
        foreign_keys=[source_id],
        back_populates="outgoing_edges",
    )
    target_territory: Mapped["Territory"] = relationship(
        foreign_keys=[target_id],
        back_populates="incoming_edges",
    )

    @property
    def weight(self) -> float:
        return self.movement_cost

    @weight.setter
    def weight(self, value: float) -> None:
        self.movement_cost = value

    @property
    def source(self) -> int:
        return self.source_id

    @source.setter
    def source(self, value: int) -> None:
        self.source_id = value

    @property
    def target(self) -> int:
        return self.target_id

    @target.setter
    def target(self, value: int) -> None:
        self.target_id = value
