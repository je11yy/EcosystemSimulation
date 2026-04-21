from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import SimulationStatus

if TYPE_CHECKING:
    from app.models.relations.simulation_agent import SimulationAgentRelation
    from app.models.relations.simulation_territory import SimulationTerritoryRelation
    from app.models.relations.simulation_user import SimulationUserRelation
    from app.models.simulation_log import SimulationLog


class Simulation(Base):
    __tablename__ = "simulations"

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'loaded', 'running', 'paused', 'stopped')",
            name="ck_simulations_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(16), default=SimulationStatus.DRAFT.value)
    tick: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user_links: Mapped[list["SimulationUserRelation"]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    territory_links: Mapped[list["SimulationTerritoryRelation"]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    agent_links: Mapped[list["SimulationAgentRelation"]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    logs: Mapped[list["SimulationLog"]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
        order_by="SimulationLog.tick",
    )

    @property
    def user_id(self) -> Optional[int]:
        return self.user_links[0].user_id if self.user_links else None

    @property
    def last_log(self) -> Optional["SimulationLog"]:
        return self.logs[-1] if self.logs else None

    @property
    def last_step(self) -> Optional[dict]:
        return self.last_log.step_result if self.last_log else None
