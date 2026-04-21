from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent


class AgentParentRelation(Base):
    __tablename__ = "agent_parent_relations"

    __table_args__ = (
        CheckConstraint("agent_id != parent_id", name="ck_agent_parent_relations_not_self"),
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    agent: Mapped["Agent"] = relationship(
        foreign_keys=[agent_id],
        back_populates="parent_links",
    )
    parent: Mapped["Agent"] = relationship(
        foreign_keys=[parent_id],
        back_populates="child_links",
    )
