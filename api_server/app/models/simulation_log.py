from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.simulation import Simulation


class SimulationLog(Base):
    __tablename__ = "simulation_logs"

    __table_args__ = (
        UniqueConstraint("simulation_id", "tick", name="uq_simulation_logs_simulation_tick"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        index=True,
    )
    tick: Mapped[int] = mapped_column(Integer, index=True)
    agent_decisions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    step_result: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    simulation: Mapped["Simulation"] = relationship(back_populates="logs")
