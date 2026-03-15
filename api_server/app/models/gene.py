from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Gene(Base):
    __tablename__ = "genes"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    gene_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    chromosome_id: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[float] = mapped_column(Float, nullable=False)

    default_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    agent = relationship("Agent", back_populates="genes")
