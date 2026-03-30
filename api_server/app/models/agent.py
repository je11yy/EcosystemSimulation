from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        index=True,
    )
    territory_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        index=True,
    )

    hunger: Mapped[int] = mapped_column(Integer, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)

    base_strength: Mapped[int] = mapped_column(Integer, nullable=False)
    base_defense: Mapped[int] = mapped_column(Integer, nullable=False)

    sex: Mapped[str] = mapped_column(String(16), nullable=False)

    species_group: Mapped[str] = mapped_column(String(128), nullable=False, default="default")

    pregnant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ticks_to_birth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    father_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    base_temp_pref: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    satisfaction: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    alive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    simulation = relationship("Simulation", back_populates="agents")

    genes = relationship("Gene", back_populates="agent", cascade="all, delete-orphan")
    gene_edges = relationship("GeneEdge", back_populates="agent", cascade="all, delete-orphan")
    gene_states = relationship("GeneState", back_populates="agent", cascade="all, delete-orphan")

    hunt_cooldown: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
