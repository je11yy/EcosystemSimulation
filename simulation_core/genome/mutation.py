from dataclasses import dataclass
from random import Random
from typing import Optional

from .effect_type import GeneEffectType
from .models import Gene, Genome


@dataclass(frozen=True)
class GenomeMutationConfig:
    # Небольшие мутации параметров генов происходят чаще всего.
    gene_parameter_rate: float = 0.08
    threshold_sigma: float = 0.08
    weight_sigma: float = 0.08

    # Переключение default_active меняет режим включения гена, поэтому редкое.
    default_active_flip_rate: float = 0.01

    # Структурные мутации графа редкие, но именно они дают новые формы генома.
    gene_duplication_rate: float = 0.01
    gene_deletion_rate: float = 0.005
    new_gene_rate: float = 0.005
    edge_addition_rate: float = 0.02
    edge_deletion_rate: float = 0.015
    edge_weight_rate: float = 0.08
    edge_weight_sigma: float = 0.08

    min_threshold: float = 0.0
    max_threshold: float = 100.0
    min_weight: float = 0.05
    max_weight: float = 3.0
    min_edge_weight: float = -3.0
    max_edge_weight: float = 3.0


@dataclass(frozen=True)
class GenomeMutationReport:
    changed_gene_parameters: int = 0
    flipped_default_active: int = 0
    duplicated_genes: int = 0
    deleted_genes: int = 0
    added_genes: int = 0
    added_edges: int = 0
    deleted_edges: int = 0
    changed_edge_weights: int = 0

    @property
    def has_mutations(self) -> bool:
        return any(self.__dict__.values())


@dataclass(frozen=True)
class GenomeMutationResult:
    genome: Genome
    report: GenomeMutationReport


class GenomeMutator:
    def __init__(self, config: Optional[GenomeMutationConfig] = None) -> None:
        self.config = config or GenomeMutationConfig()

    def mutate(
        self,
        genome: Genome,
        rng: Optional[Random] = None,
    ) -> GenomeMutationResult:
        rng = rng or Random()
        mutated = _clone_genome(genome)

        changed_gene_parameters = self._mutate_gene_parameters(mutated, rng)
        flipped_default_active = self._mutate_default_active(mutated, rng)
        deleted_genes = self._delete_genes(mutated, rng)
        duplicated_genes = self._duplicate_genes(mutated, rng)
        added_genes = self._add_new_gene(mutated, rng)
        deleted_edges = self._delete_edges(mutated, rng)
        changed_edge_weights = self._mutate_edge_weights(mutated, rng)
        added_edges = self._add_edge(mutated, rng)

        mutated._sync_edges_from_graph()

        return GenomeMutationResult(
            genome=mutated,
            report=GenomeMutationReport(
                changed_gene_parameters=changed_gene_parameters,
                flipped_default_active=flipped_default_active,
                duplicated_genes=duplicated_genes,
                deleted_genes=deleted_genes,
                added_genes=added_genes,
                added_edges=added_edges,
                deleted_edges=deleted_edges,
                changed_edge_weights=changed_edge_weights,
            ),
        )

    def _mutate_gene_parameters(self, genome: Genome, rng: Random) -> int:
        changed = 0
        for gene_id, gene in list(genome.genes.items()):
            if rng.random() > self.config.gene_parameter_rate:
                continue

            genome.genes[gene_id] = Gene(
                id=gene.id,
                name=gene.name,
                effect_type=gene.effect_type,
                threshold=_clamp(
                    gene.threshold + rng.gauss(0.0, self.config.threshold_sigma),
                    self.config.min_threshold,
                    self.config.max_threshold,
                ),
                weight=_clamp(
                    gene.weight + rng.gauss(0.0, self.config.weight_sigma),
                    self.config.min_weight,
                    self.config.max_weight,
                ),
                default_active=gene.default_active,
                is_active=False,
            )
            changed += 1

        return changed

    def _mutate_default_active(self, genome: Genome, rng: Random) -> int:
        changed = 0
        for gene_id, gene in list(genome.genes.items()):
            if rng.random() > self.config.default_active_flip_rate:
                continue

            genome.genes[gene_id] = Gene(
                id=gene.id,
                name=gene.name,
                effect_type=gene.effect_type,
                threshold=gene.threshold,
                weight=gene.weight,
                default_active=not gene.default_active,
                is_active=False,
            )
            changed += 1

        return changed

    def _delete_genes(self, genome: Genome, rng: Random) -> int:
        deleted = 0
        for gene_id in list(genome.genes):
            if len(genome.genes) <= 1:
                break
            if rng.random() > self.config.gene_deletion_rate:
                continue

            del genome.genes[gene_id]
            genome.graph.nodes.discard(gene_id)
            genome.graph.outgoing.pop(gene_id, None)
            genome.graph.edges = {
                key: edge
                for key, edge in genome.graph.edges.items()
                if edge.source_id != gene_id and edge.target_id != gene_id
            }
            _rebuild_outgoing(genome)
            deleted += 1

        return deleted

    def _duplicate_genes(self, genome: Genome, rng: Random) -> int:
        duplicated = 0
        for gene in list(genome.genes.values()):
            if rng.random() > self.config.gene_duplication_rate:
                continue

            duplicated_gene = Gene(
                id=_next_gene_id(genome),
                name=f"{gene.name} copy",
                effect_type=gene.effect_type,
                threshold=gene.threshold,
                weight=gene.weight,
                default_active=gene.default_active,
                is_active=False,
            )
            genome.add_gene(duplicated_gene)
            duplicated += 1

        return duplicated

    def _add_new_gene(self, genome: Genome, rng: Random) -> int:
        if rng.random() > self.config.new_gene_rate:
            return 0

        effect_type = rng.choice(list(GeneEffectType))
        genome.add_gene(
            Gene(
                id=_next_gene_id(genome),
                name=f"Mutated {effect_type.value}",
                effect_type=effect_type,
                threshold=rng.uniform(self.config.min_threshold, self.config.max_threshold),
                weight=rng.uniform(0.7, 1.3),
                default_active=rng.random() < 0.25,
                is_active=False,
            )
        )
        return 1

    def _delete_edges(self, genome: Genome, rng: Random) -> int:
        deleted = 0
        for key in list(genome.graph.edges):
            if rng.random() > self.config.edge_deletion_rate:
                continue
            del genome.graph.edges[key]
            deleted += 1

        if deleted:
            _rebuild_outgoing(genome)

        return deleted

    def _mutate_edge_weights(self, genome: Genome, rng: Random) -> int:
        changed = 0
        for edge in list(genome.graph.edges.values()):
            if rng.random() > self.config.edge_weight_rate:
                continue

            genome.graph.add_edge(
                edge.source_id,
                edge.target_id,
                _clamp(
                    edge.weight + rng.gauss(0.0, self.config.edge_weight_sigma),
                    self.config.min_edge_weight,
                    self.config.max_edge_weight,
                ),
            )
            changed += 1

        return changed

    def _add_edge(self, genome: Genome, rng: Random) -> int:
        if len(genome.genes) < 2 or rng.random() > self.config.edge_addition_rate:
            return 0

        source_id, target_id = rng.sample(list(genome.genes), 2)
        if genome.graph.get_edge(source_id, target_id) is not None:
            return 0

        genome.add_edge(
            source_id,
            target_id,
            rng.uniform(self.config.min_edge_weight, self.config.max_edge_weight),
        )
        return 1


def _clone_genome(genome: Genome) -> Genome:
    cloned = Genome()
    for gene in genome.genes.values():
        cloned.add_gene(
            Gene(
                id=gene.id,
                name=gene.name,
                effect_type=gene.effect_type,
                threshold=gene.threshold,
                weight=gene.weight,
                default_active=gene.default_active,
                is_active=False,
            )
        )

    for edge in genome.graph.edges.values():
        cloned.add_edge(edge.source_id, edge.target_id, edge.weight)

    return cloned


def _rebuild_outgoing(genome: Genome) -> None:
    genome.graph.outgoing = {gene_id: [] for gene_id in genome.genes}
    for edge in genome.graph.edges.values():
        genome.graph.outgoing.setdefault(edge.source_id, []).append(edge)


def _next_gene_id(genome: Genome) -> int:
    if not genome.genes:
        return 1
    return max(genome.genes) + 1


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
