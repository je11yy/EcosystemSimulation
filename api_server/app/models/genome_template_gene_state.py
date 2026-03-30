from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GenomeTemplateGeneState(Base):
    __tablename__ = "genome_template_gene_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    genome_template_id: Mapped[int] = mapped_column(
        ForeignKey("genome_templates.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    gene_id = Column(Integer, ForeignKey("genome_template_genes.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    genome_template = relationship("GenomeTemplate", back_populates="gene_states")
