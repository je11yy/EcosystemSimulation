from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent import Agent
    from app.models.genome.genome import Genome


class GenomeAgentRelation(Base):
    __tablename__ = "genome_agent_relations"

    __table_args__ = (UniqueConstraint("agent_id", name="uq_genome_agent_relations_agent"),)

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genome_id: Mapped[int] = mapped_column(
        ForeignKey("genomes.id", ondelete="RESTRICT"),
        primary_key=True,
    )

    agent: Mapped["Agent"] = relationship(back_populates="genome_links")
    genome: Mapped["Genome"] = relationship(back_populates="agent_links")
