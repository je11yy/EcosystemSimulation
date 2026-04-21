from typing import Optional

from pydantic import BaseModel


class RuntimeTerritoryEdge(BaseModel):
    id: Optional[int] = None
    source: int
    target: int
    weight: float = 1.0
