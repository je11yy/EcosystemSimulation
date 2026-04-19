from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.genome.gene import Gene


class GeneEdge(Base):
    __tablename__ = "gene_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("genes.id", ondelete="CASCADE"), index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("genes.id", ondelete="CASCADE"), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    source_gene: Mapped["Gene"] = relationship(
        foreign_keys=[source_id],
        back_populates="outgoing_edges",
    )
    target_gene: Mapped["Gene"] = relationship(
        foreign_keys=[target_id],
        back_populates="incoming_edges",
    )

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
