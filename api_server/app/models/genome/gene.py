from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import GeneEffectType

if TYPE_CHECKING:
    from app.models.genome.edge import GeneEdge
    from app.models.relations.genome_gene import GenomeGeneRelation


class Gene(Base):
    __tablename__ = "genes"

    __table_args__ = (
        CheckConstraint(
            "effect_type IN "
            "('hunger', 'hp', 'strength', 'defense', 'temp_pref', 'satisfaction', 'hunt_cooldown')",
            name="ck_genes_effect_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    effect_type: Mapped[str] = mapped_column(
        String(64),
        default=GeneEffectType.STRENGTH.value,
        index=True,
    )
    x: Mapped[float] = mapped_column(Float, default=0.0)
    y: Mapped[float] = mapped_column(Float, default=0.0)
    default_active: Mapped[bool] = mapped_column(Boolean, default=True)
    threshold: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    genome_links: Mapped[list["GenomeGeneRelation"]] = relationship(
        back_populates="gene",
        cascade="all, delete-orphan",
    )
    outgoing_edges: Mapped[list["GeneEdge"]] = relationship(
        foreign_keys="GeneEdge.source_id",
        back_populates="source_gene",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list["GeneEdge"]] = relationship(
        foreign_keys="GeneEdge.target_id",
        back_populates="target_gene",
        cascade="all, delete-orphan",
    )

    @property
    def position(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}
