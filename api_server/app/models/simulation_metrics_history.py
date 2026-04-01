from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SimulationMetricsHistory(Base):
    __tablename__ = "simulation_metrics_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tick: Mapped[int] = mapped_column(Integer, nullable=False)

    alive_population: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_hunger_alive: Mapped[float] = mapped_column(Float, nullable=False)
    avg_hp_alive: Mapped[float] = mapped_column(Float, nullable=False)
    avg_hunt_cooldown_alive: Mapped[float] = mapped_column(Float, nullable=False)
    successful_hunts: Mapped[int] = mapped_column(Integer, nullable=False)
    births_count: Mapped[int] = mapped_column(Integer, nullable=False)
    deaths_count: Mapped[int] = mapped_column(Integer, nullable=False)

    population_by_species_group: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    occupancy_by_territory: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    action_counts: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    deaths_by_reason: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    simulation = relationship("Simulation", back_populates="metrics_history")
