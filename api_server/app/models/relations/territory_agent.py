from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.territory.territory import Territory


class TerritoryAgentRelation(Base):
    __tablename__ = "territory_agent_relations"

    __table_args__ = (UniqueConstraint("agent_id", name="uq_territory_agent_relations_agent"),)

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    territory_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        primary_key=True,
    )

    agent: Mapped["Agent"] = relationship(back_populates="territory_links")
    territory: Mapped["Territory"] = relationship(back_populates="agent_links")
