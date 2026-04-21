from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class WeightedEdge:
    source_id: int
    target_id: int
    weight: float

    @property
    def key(self) -> Tuple[int, int]:
        return (self.source_id, self.target_id)


class WeightedGraph:
    def __init__(self) -> None:
        self.nodes: Set[int] = set()
        self.edges: Dict[Tuple[int, int], WeightedEdge] = {}
        self.outgoing: Dict[int, List[WeightedEdge]] = {}

    def add_node(self, node_id: int) -> None:
        self.nodes.add(node_id)
        self.outgoing.setdefault(node_id, [])

    def add_edge(self, source_id: int, target_id: int, weight: float) -> None:
        if source_id not in self.nodes:
            raise ValueError(f"Unknown source node: {source_id}")
        if target_id not in self.nodes:
            raise ValueError(f"Unknown target node: {target_id}")

        edge = WeightedEdge(source_id=source_id, target_id=target_id, weight=weight)
        key = edge.key

        if key in self.edges:
            self.outgoing[source_id] = [
                outgoing_edge
                for outgoing_edge in self.outgoing[source_id]
                if outgoing_edge.key != key
            ]

        self.edges[key] = edge
        self.outgoing[source_id].append(edge)

    def get_edge(self, source_id: int, target_id: int) -> Optional[WeightedEdge]:
        return self.edges.get((source_id, target_id))

    def get_neighbors(self, node_id: int) -> List[WeightedEdge]:
        return list(self.outgoing.get(node_id, []))

    def copy(self) -> "WeightedGraph":
        graph = WeightedGraph()
        for node_id in self.nodes:
            graph.add_node(node_id)
        for edge in self.edges.values():
            graph.add_edge(edge.source_id, edge.target_id, edge.weight)
        return graph
