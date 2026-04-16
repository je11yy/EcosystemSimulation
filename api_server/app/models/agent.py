from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import AgentSex

if TYPE_CHECKING:
    from app.models.relations.agent_parent import AgentParentRelation
    from app.models.relations.genome_agent import GenomeAgentRelation
    from app.models.relations.simulation_agent import SimulationAgentRelation
    from app.models.relations.territory_agent import TerritoryAgentRelation


class Agent(Base):
    __tablename__ = "agents"

    __table_args__ = (
        CheckConstraint("sex IN ('male', 'female')", name="ck_agents_sex"),
        CheckConstraint("hunger >= 0", name="ck_agents_hunger_non_negative"),
        CheckConstraint("hp >= 0", name="ck_agents_hp_non_negative"),
        CheckConstraint("hunt_cooldown >= 0", name="ck_agents_hunt_cooldown_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sex: Mapped[str] = mapped_column(String(16), default=AgentSex.MALE.value)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=True)
    hunger: Mapped[float] = mapped_column(Float, default=0.0)
    hp: Mapped[float] = mapped_column(Float, default=100.0)
    is_pregnant: Mapped[bool] = mapped_column(Boolean, default=False)
    ticks_to_birth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    satisfaction: Mapped[float] = mapped_column(Float, default=0.0)
    hunt_cooldown: Mapped[int] = mapped_column(Integer, default=0)
    strength: Mapped[float] = mapped_column(Float, default=1.0)
    defense: Mapped[float] = mapped_column(Float, default=1.0)
    temp_pref: Mapped[float] = mapped_column(Float, default=20.0)

    simulation_links: Mapped[list["SimulationAgentRelation"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    territory_links: Mapped[list["TerritoryAgentRelation"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    genome_links: Mapped[list["GenomeAgentRelation"]] = relationship(
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    parent_links: Mapped[list["AgentParentRelation"]] = relationship(
        foreign_keys="AgentParentRelation.agent_id",
        back_populates="agent",
        cascade="all, delete-orphan",
    )
    child_links: Mapped[list["AgentParentRelation"]] = relationship(
        foreign_keys="AgentParentRelation.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    @property
    def pregnant(self) -> bool:
        return self.is_pregnant

    @pregnant.setter
    def pregnant(self, value: bool) -> None:
        self.is_pregnant = value

    @property
    def territory_id(self) -> Optional[int]:
        return self.territory_links[0].territory_id if self.territory_links else None

    @property
    def genome_id(self) -> Optional[int]:
        return self.genome_links[0].genome_id if self.genome_links else None
