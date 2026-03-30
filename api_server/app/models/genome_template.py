from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GenomeTemplate(Base):
    __tablename__ = "genome_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # для видовой принадлежности
    species_group: Mapped[str] = mapped_column(String(128), nullable=False, default="default")

    # задел под поведенческий профиль
    base_predation_drive: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    genes = relationship(
        "GenomeTemplateGene",
        back_populates="genome_template",
        cascade="all, delete-orphan",
    )
    edges = relationship(
        "GenomeTemplateEdge",
        back_populates="genome_template",
        cascade="all, delete-orphan",
    )
    gene_states = relationship(
        "GenomeTemplateGeneState",
        back_populates="genome_template",
        cascade="all, delete-orphan",
    )
