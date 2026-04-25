from dataclasses import dataclass, field
from typing import Dict

from ...graph import WeightedGraph
from .edge import GeneEdge
from .gene import Gene


@dataclass
class Genome:
    genes: Dict[int, Gene] = field(default_factory=dict)
    edges: Dict[int, GeneEdge] = field(default_factory=dict)
    graph: WeightedGraph = field(default_factory=WeightedGraph)

    def __post_init__(self) -> None:
        for gene_id in self.genes:
            self.graph.add_node(gene_id)

        for edge in self.edges.values():
            self.graph.add_edge(edge.source_id, edge.target_id, edge.weight)

        if not self.edges:
            self._sync_edges_from_graph()

    def add_gene(self, gene: Gene) -> None:
        if any(existing.effect_type == gene.effect_type for existing in self.genes.values()):
            raise ValueError(f"Duplicate gene effect type: {gene.effect_type.value}")
        self.genes[gene.id] = gene
        self.graph.add_node(gene.id)

    def add_edge(self, source_id: int, target_id: int, weight: float) -> None:
        self.graph.add_edge(source_id, target_id, weight)
        self._sync_edges_from_graph()

    def outgoing_genes(self, gene_id: int) -> Dict[int, float]:
        return {edge.target_id: edge.weight for edge in self.graph.get_neighbors(gene_id)}

    def _sync_edges_from_graph(self) -> None:
        self.edges = {
            index: GeneEdge(edge.source_id, edge.target_id, edge.weight)
            for index, edge in enumerate(self.graph.edges.values(), start=1)
        }
