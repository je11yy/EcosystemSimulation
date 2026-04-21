from pydantic import BaseModel


class Edge(BaseModel):
    id: int
    source: int
    target: int
    weight: float


class GeneEdge(Edge):
    pass


class GeneEdgeCreate(BaseModel):
    source: int
    target: int
    weight: float
