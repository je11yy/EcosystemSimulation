from dataclasses import dataclass, field
from typing import Dict, List, Mapping

from ..graph import WeightedGraph
from .territory_state import TerritoryState


@dataclass
class WorldState:
    territories: Dict[int, TerritoryState] = field(default_factory=dict)
    graph: WeightedGraph = field(default_factory=WeightedGraph)

    def __post_init__(self) -> None:
        for territory in self.territories.values():
            territory.validate()
            self.graph.add_node(territory.id)

    def add_territory(self, territory: TerritoryState) -> None:
        territory.validate()
        self.territories[territory.id] = territory
        self.graph.add_node(territory.id)

    def get_territory(self, territory_id: int) -> TerritoryState:
        return self.territories[territory_id]

    def all_territories(self) -> List[TerritoryState]:
        return list(self.territories.values())

    def territory_by_id(self) -> Mapping[int, TerritoryState]:
        return self.territories

    def add_edge(self, source_id: int, target_id: int, weight: float) -> None:
        self.graph.add_edge(source_id, target_id, weight)

    def get_neighbors(self, territory_id: int) -> Dict[int, float]:
        return {edge.target_id: edge.weight for edge in self.graph.get_neighbors(territory_id)}

    def regenerate_food(self) -> None:
        for territory in self.territories.values():
            territory.regenerate_food()
