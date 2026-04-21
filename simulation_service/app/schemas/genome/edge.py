from typing import Optional

from pydantic import BaseModel


class RuntimeGeneEdge(BaseModel):
    id: Optional[int] = None
    source: int
    target: int
    weight: float = 1.0
