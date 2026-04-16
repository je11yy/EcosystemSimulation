from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.relations.genome_agent import GenomeAgentRelation
    from app.models.relations.genome_gene import GenomeGeneRelation
    from app.models.relations.genome_user import GenomeUserRelation


class Genome(Base):
    __tablename__ = "genomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user_links: Mapped[list["GenomeUserRelation"]] = relationship(
        back_populates="genome",
        cascade="all, delete-orphan",
    )
    gene_links: Mapped[list["GenomeGeneRelation"]] = relationship(
        back_populates="genome",
        cascade="all, delete-orphan",
    )
    agent_links: Mapped[list["GenomeAgentRelation"]] = relationship(
        back_populates="genome",
        cascade="all, delete-orphan",
    )

    @property
    def user_id(self) -> Optional[int]:
        return self.user_links[0].user_id if self.user_links else None
