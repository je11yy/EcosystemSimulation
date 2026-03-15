import random
from dataclasses import dataclass, replace
from typing import Protocol, runtime_checkable

from simulation_core.agents.genome.edge import GeneEdge
from simulation_core.agents.genome.gene import Gene
from simulation_core.agents.genome.genome import Genome


@runtime_checkable
class MutationModel(Protocol):
    def mutate(
        self,
        genome: Genome,
        rng: random.Random,
    ) -> Genome: ...


@dataclass(frozen=True)
class SimpleMutationModel(MutationModel):
    """
    Простая модель мутаций:
    - gene threshold mutation
    - edge weight mutation
    - edge add/remove mutation
    """

    gene_threshold_mutation_probability: float = 0.1
    edge_weight_mutation_probability: float = 0.1
    edge_add_probability: float = 0.03
    edge_remove_probability: float = 0.03

    threshold_mutation_std: float = 0.2
    edge_weight_mutation_std: float = 0.2

    def mutate(
        self,
        genome: Genome,
        rng: random.Random,
    ) -> Genome:
        mutated = Genome()

        # 1. мутируем гены
        for gene in genome.all_genes():
            mutated_gene = self._mutate_gene(gene, rng)
            mutated.add_gene(mutated_gene)

        # 2. мутируем уже существующие рёбра
        for edge in genome.edges:
            if rng.random() < self.edge_remove_probability:
                continue

            mutated_edge = self._mutate_edge(edge, rng)
            mutated.add_edge(mutated_edge)

        # 3. иногда добавляем новое ребро
        self._maybe_add_random_edge(mutated, rng)

        return mutated

    def _mutate_gene(
        self,
        gene: Gene,
        rng: random.Random,
    ) -> Gene:
        if rng.random() >= self.gene_threshold_mutation_probability:
            return gene

        delta = rng.gauss(0.0, self.threshold_mutation_std)

        return replace(
            gene,
            threshold=gene.threshold + delta,
        )

    def _mutate_edge(
        self,
        edge: GeneEdge,
        rng: random.Random,
    ) -> GeneEdge:
        if rng.random() >= self.edge_weight_mutation_probability:
            return edge

        delta = rng.gauss(0.0, self.edge_weight_mutation_std)

        return replace(
            edge,
            weight=edge.weight + delta,
        )

    def _maybe_add_random_edge(
        self,
        genome: Genome,
        rng: random.Random,
    ) -> None:
        if rng.random() >= self.edge_add_probability:
            return

        genes = genome.all_genes()
        if len(genes) < 2:
            return

        source = rng.choice(genes)
        target = rng.choice(genes)

        if source.id == target.id:
            return

        existing = any(
            edge.source_gene_id == source.id and edge.target_gene_id == target.id
            for edge in genome.edges
        )
        if existing:
            return

        new_edge = GeneEdge(
            source_gene_id=source.id,
            target_gene_id=target.id,
            weight=rng.gauss(0.0, 0.5),
        )
        genome.add_edge(new_edge)
