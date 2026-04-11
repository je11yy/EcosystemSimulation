from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SimulationLastStep(Base):
    __tablename__ = "simulation_last_step"

    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tick: Mapped[int] = mapped_column(Integer, nullable=False)
    step_result: Mapped[dict] = mapped_column(JSONB, nullable=False)

    simulation = relationship("Simulation", back_populates="last_step")
