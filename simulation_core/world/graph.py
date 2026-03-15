from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from simulation_core.types import TerritoryId


@dataclass(frozen=True)
class Edge:
    """Ребро графа территорий - связь между двумя территориями.

    Представляет возможность перемещения между территориями
    с определенной стоимостью.
    """

    to: TerritoryId  # ID целевой территории
    cost: float = 1.0  # Стоимость перемещения (может влиять на голод или другие параметры)


@runtime_checkable
class TerritoryGraph(Protocol):
    """Протокол для графа связей между территориями.

    Определяет интерфейс для получения соседей территории.
    """

    def neighbors(self, territory_id: TerritoryId) -> Sequence[Edge]: ...


class AdjacencyListGraph:
    """Реализация графа территорий на основе списка смежности.

    Хранит связи между территориями в виде словаря,
    где ключ - ID территории, значение - список соседей.
    """

    def __init__(self) -> None:
        self._adj: dict[TerritoryId, list[Edge]] = {}  # Словарь смежности

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
