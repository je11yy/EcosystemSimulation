from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.relations.genome_user import GenomeUserRelation
    from app.models.relations.simulation_user import SimulationUserRelation


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    simulation_links: Mapped[list["SimulationUserRelation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    genome_links: Mapped[list["GenomeUserRelation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
