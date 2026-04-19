from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .edge import GeneEdge, GeneEdgeCreate
from .gene import Gene, GeneCreate


class AvailableGenome(BaseModel):
    id: int
    name: str


class GenomeRead(AvailableGenome):
    genes: List[Gene] = []
    edges: List[GeneEdge] = []

    class Config:
        from_attributes = True


class GenomeList(BaseModel):
    id: int
    name: str
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class GenomeCreate(BaseModel):
    name: str
    user_id: Optional[int] = None


__all__ = [
    "AvailableGenome",
    "Gene",
    "GeneCreate",
    "GeneEdge",
    "GeneEdgeCreate",
    "GenomeCreate",
    "GenomeList",
    "GenomeRead",
]
