from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TerritoryEdge(Base):
    __tablename__ = "territory_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        index=True,
    )

    source_territory_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        index=True,
    )
    target_territory_id: Mapped[int] = mapped_column(
        ForeignKey("territories.id", ondelete="CASCADE"),
        index=True,
    )

    movement_cost: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    simulation = relationship("Simulation", back_populates="territory_edges")
