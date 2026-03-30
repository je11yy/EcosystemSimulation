from dataclasses import dataclass, field
from typing import List

from simulation_core.agents.genome.edge import GeneEdge
from simulation_core.agents.genome.gene import Gene
from simulation_core.agents.genome.state import GenomeState


@dataclass
class ChromosomeView:
    chromosome_id: str
    genes: List[Gene]


@dataclass
class Genome:
    """Геном агента, представленный как ориентированный взвешенный граф.

    Геном состоит из генов (узлов) и связей между ними (ребер).
    Гены могут активироваться/деактивироваться в зависимости от входных сигналов
    и связей с другими генами.
    """

    genes: dict[int, Gene] = field(default_factory=lambda: dict[int, Gene]())  # Гены по ID
    edges: list[GeneEdge] = field(default_factory=lambda: list[GeneEdge]())  # Связи между генами

    def add_gene(self, gene: Gene) -> None:
        self.genes[gene.id] = gene

    def add_edge(self, edge: GeneEdge) -> None:
        if edge.source_gene_id not in self.genes:
            raise ValueError(f"Unknown source gene: {edge.source_gene_id}")
        if edge.target_gene_id not in self.genes:
            raise ValueError(f"Unknown target gene: {edge.target_gene_id}")
        self.edges.append(edge)

    def get_gene(self, gene_id: int) -> Gene:
        return self.genes[gene_id]

    def all_genes(self) -> list[Gene]:
        return list(self.genes.values())

    def incoming_edges(self, gene_id: int) -> list[GeneEdge]:
        # Получает все входящие связи для гена.
        return [edge for edge in self.edges if edge.target_gene_id == gene_id]

    def outgoing_edges(self, gene_id: int) -> list[GeneEdge]:
        # Получает все исходящие связи для гена.
        return [edge for edge in self.edges if edge.source_gene_id == gene_id]

    def build_default_state(self) -> GenomeState:
        # Создает начальное состояние генома.
        return GenomeState(
            gene_activity={gene.id: gene.default_active for gene in self.genes.values()}
        )

    def chromosome_ids(self) -> list[str]:
        return sorted({gene.chromosome_id for gene in self.genes.values()})

    def genes_on_chromosome(self, chromosome_id: str) -> list[Gene]:
        genes = [gene for gene in self.genes.values() if gene.chromosome_id == chromosome_id]
        return sorted(genes, key=lambda g: g.position)

    def chromosomes(self) -> list[ChromosomeView]:
        return [
            ChromosomeView(
                chromosome_id=chromosome_id,
                genes=self.genes_on_chromosome(chromosome_id),
            )
            for chromosome_id in self.chromosome_ids()
        ]
