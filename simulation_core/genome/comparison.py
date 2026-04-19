from dataclasses import dataclass
from typing import Set, Tuple

from .models import Gene, Genome

GeneSignature = Tuple[str, float, float, bool]
EdgeSignature = Tuple[GeneSignature, GeneSignature, float]


@dataclass(frozen=True)
class GenomeDiff:
    added_genes: Set[GeneSignature]
    removed_genes: Set[GeneSignature]
    added_edges: Set[EdgeSignature]
    removed_edges: Set[EdgeSignature]

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added_genes or self.removed_genes or self.added_edges or self.removed_edges
        )


class GenomeComparator:
    def compare(self, left: Genome, right: Genome) -> GenomeDiff:
        left_genes = _gene_signatures(left)
        right_genes = _gene_signatures(right)
        left_edges = _edge_signatures(left)
        right_edges = _edge_signatures(right)

        return GenomeDiff(
            added_genes=right_genes - left_genes,
            removed_genes=left_genes - right_genes,
            added_edges=right_edges - left_edges,
            removed_edges=left_edges - right_edges,
        )


def _gene_signature(gene: Gene) -> GeneSignature:
    effect_type = getattr(gene.effect_type, "value", gene.effect_type)
    return (
        effect_type,
        round(gene.threshold, 4),
        round(gene.weight, 4),
        gene.default_active,
    )


def _gene_signatures(genome: Genome) -> Set[GeneSignature]:
    return {_gene_signature(gene) for gene in genome.genes.values()}


def _edge_signatures(genome: Genome) -> Set[EdgeSignature]:
    signatures = set()
    for edge in genome.graph.edges.values():
        source_gene = genome.genes.get(edge.source_id)
        target_gene = genome.genes.get(edge.target_id)
        if source_gene is None or target_gene is None:
            continue
        signatures.add(
            (
                _gene_signature(source_gene),
                _gene_signature(target_gene),
                round(edge.weight, 4),
            )
        )
    return signatures
