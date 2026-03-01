from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from simulation_core.types import TerritoryId


@dataclass(frozen=True)
class Edge:
    to: TerritoryId
    cost: float = 1.0  # стоимость перемещения (возможно, количество убавления сытости?)


@runtime_checkable
class TerritoryGraph(Protocol):
    """
    Граф связей территорий
    """

    def neighbors(self, territory_id: TerritoryId) -> Sequence[Edge]: ...


class AdjacencyListGraph:
    """
    Реализация графа связей территорий на основе списка смежности
    """

    def __init__(self) -> None:
        self._adj: dict[TerritoryId, list[Edge]] = {}

    def add_node(self, tid: TerritoryId) -> None:
        self._adj.setdefault(tid, [])

    def add_edge(
        self, a: TerritoryId, b: TerritoryId, cost: float = 1.0, bidirectional: bool = True
    ) -> None:
        self.add_node(a)
        self.add_node(b)
        self._adj[a].append(Edge(to=b, cost=cost))
        if bidirectional:
            self._adj[b].append(Edge(to=a, cost=cost))

    def neighbors(self, territory_id: TerritoryId) -> Sequence[Edge]:
        return self._adj.get(territory_id, [])
