from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GenomeTemplateEdge(Base):
    __tablename__ = "genome_template_edges"

    id: Mapped[int] = mapped_column(primary_key=True)
    genome_template_id: Mapped[int] = mapped_column(
        ForeignKey("genome_templates.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    source_gene_id: Mapped[int] = mapped_column(Integer, nullable=False)
    target_gene_id: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    genome_template = relationship("GenomeTemplate", back_populates="edges")
