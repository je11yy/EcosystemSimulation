from pydantic import BaseModel


class Edge(BaseModel):
    id: int
    source: int
    target: int
    weight: float


class TerritoryEdge(Edge):
    pass
