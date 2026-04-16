from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .edge import GeneEdge
from .gene import Gene


class AvailableGenome(BaseModel):
    """Available genome basic info"""

    id: int
    name: str


class GenomeRead(AvailableGenome):
    """Genome read response with genes and edges"""

    genes: List[Gene] = []
    edges: List[GeneEdge] = []

    class Config:
        from_attributes = True


class GenomeList(BaseModel):
    """Genome list item with metadata"""

    id: int
    name: str
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class GenomeCreate(BaseModel):
    """Genome create request"""

    name: str
    user_id: Optional[int] = None
