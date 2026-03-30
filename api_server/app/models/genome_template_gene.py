from typing import Optional

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from simulation_core.agents.genome.effect_type import GeneEffectType


class GenomeTemplateGene(Base):
    __tablename__ = "genome_template_genes"

    id: Mapped[int] = mapped_column(primary_key=True)
    genome_template_id: Mapped[int] = mapped_column(
        ForeignKey("genome_templates.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    chromosome_id: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[float] = mapped_column(Float, nullable=False)

    default_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    x: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    y: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    effect_type: Mapped[GeneEffectType] = mapped_column(
        Enum(GeneEffectType),
        nullable=False,
    )

    genome_template = relationship("GenomeTemplate", back_populates="genes")
