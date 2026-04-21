from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.simulation import Simulation
    from app.models.user import User


class SimulationUserRelation(Base):
    __tablename__ = "simulation_user_relations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(back_populates="simulation_links")
    simulation: Mapped["Simulation"] = relationship(back_populates="user_links")
