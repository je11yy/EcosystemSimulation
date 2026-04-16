from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.genome.gene import Gene
    from app.models.genome.genome import Genome


class GenomeGeneRelation(Base):
    __tablename__ = "genome_gene_relations"

    genome_id: Mapped[int] = mapped_column(
        ForeignKey("genomes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    gene_id: Mapped[int] = mapped_column(
        ForeignKey("genes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    genome: Mapped["Genome"] = relationship(back_populates="gene_links")
    gene: Mapped["Gene"] = relationship(back_populates="genome_links")
