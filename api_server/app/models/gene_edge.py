from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GeneEdge(Base):
    __tablename__ = "gene_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    source_gene_key: Mapped[str] = mapped_column(String(128), nullable=False)
    target_gene_key: Mapped[str] = mapped_column(String(128), nullable=False)

    weight: Mapped[float] = mapped_column(Float, nullable=False)

    agent = relationship("Agent", back_populates="gene_edges")
