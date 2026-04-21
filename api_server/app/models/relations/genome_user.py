from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.genome.genome import Genome
    from app.models.user import User


class GenomeUserRelation(Base):
    __tablename__ = "genome_user_relations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    genome_id: Mapped[int] = mapped_column(
        ForeignKey("genomes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(back_populates="genome_links")
    genome: Mapped["Genome"] = relationship(back_populates="user_links")
