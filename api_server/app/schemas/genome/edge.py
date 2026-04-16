from pydantic import BaseModel


class Edge(BaseModel):  # type: ignore
    """Graph edge"""

    id: int
    source: int
    target: int
    weight: float


class GeneEdge(Edge):
    """Gene edge in genome"""

    pass
