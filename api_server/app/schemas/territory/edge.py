from pydantic import BaseModel


class Edge(BaseModel):  # type: ignore
    """Graph edge"""

    id: int
    source: int
    target: int
    weight: float


class TerritoryEdge(Edge):
    """Alias for Edge used in territory context"""

    pass
