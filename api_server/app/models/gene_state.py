from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class GeneState(Base):
    __tablename__ = "gene_states"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(64), ForeignKey("agents.id"))
    gene_id = Column(String(64))
    is_active = Column(Boolean, default=True)

    agent = relationship("Agent", back_populates="gene_states")
