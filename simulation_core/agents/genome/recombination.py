import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from simulation_core.agents.genome.edge import GeneEdge
from simulation_core.agents.genome.gene import Gene
from simulation_core.agents.genome.genome import Genome


@runtime_checkable
class RecombinationModel(Protocol):
    def recombine(
        self,
        parent_a: Genome,
        parent_b: Genome,
        rng: random.Random,
    ) -> Genome: ...


@dataclass(frozen=True)
class SingleCrossoverRecombinationModel(RecombinationModel):
    """
    Простая модель:
    - для каждой хромосомы выбирается одна точка crossover
    - до неё гены берутся от одного родителя
    - после неё от другого

    Предполагается, что:
    - у родителей одинаковый набор gene_id
    - gene_id совпадает между родителями
    - chromosome_id и порядок gene_id сопоставимы
    """

    inherit_shared_edges_probability: float = 1.0
    inherit_unique_edge_probability: float = 0.5

    def recombine(
        self,
        parent_a: Genome,
        parent_b: Genome,
        rng: random.Random,
    ) -> Genome:
        child = Genome()

        inherited_gene_ids: set[str] = set()

        chromosome_ids = sorted(set(parent_a.chromosome_ids()) | set(parent_b.chromosome_ids()))

        for chromosome_id in chromosome_ids:
            a_genes = parent_a.genes_on_chromosome(chromosome_id)
            b_genes = parent_b.genes_on_chromosome(chromosome_id)

            if not a_genes and not b_genes:
                continue

            if len(a_genes) != len(b_genes):
                raise ValueError(
                    f"Chromosome '{chromosome_id}' has different gene counts in parents"
                )

            if [g.id for g in a_genes] != [g.id for g in b_genes]:
                raise ValueError(
                    f"Chromosome '{chromosome_id}' has different gene order in parents"
                )

            inherited_genes = self._recombine_chromosome(
                genes_a=a_genes,
                genes_b=b_genes,
                rng=rng,
            )

            for gene in inherited_genes:
                child.add_gene(gene)
                inherited_gene_ids.add(gene.id)

        inherited_edges = self._inherit_edges(
            parent_a=parent_a,
            parent_b=parent_b,
            inherited_gene_ids=inherited_gene_ids,
            rng=rng,
        )

        for edge in inherited_edges:
            child.add_edge(edge)

        return child

    def _recombine_chromosome(
        self,
        genes_a: list[Gene],
        genes_b: list[Gene],
        rng: random.Random,
    ) -> list[Gene]:
        """
        Возвращает список генов ребёнка для одной хромосомы.
        """

        if len(genes_a) != len(genes_b):
            raise ValueError("Parents must have the same number of genes on chromosome")

        n = len(genes_a)

        if n == 0:
            return []

        if n == 1:
            return [rng.choice([genes_a[0], genes_b[0]])]

        start_with_a = rng.choice([True, False])

        # crossover_index означает:
        # гены с индексом < crossover_index берём от первого выбранного родителя
        # остальные — от второго
        crossover_index = rng.randint(1, n - 1)

        child_genes: list[Gene] = []

        for idx in range(n):
            if idx < crossover_index:
                chosen_gene = genes_a[idx] if start_with_a else genes_b[idx]
            else:
                chosen_gene = genes_b[idx] if start_with_a else genes_a[idx]

            child_genes.append(chosen_gene)

        return child_genes

    def _inherit_edges(
        self,
        parent_a: Genome,
        parent_b: Genome,
        inherited_gene_ids: set[str],
        rng: random.Random,
    ) -> list[GeneEdge]:
        """
        Наследование регуляторных рёбер:
        - если ребро есть у обоих родителей, почти всегда сохраняем
        - если только у одного, сохраняем вероятностно
        """

        a_edges = {
            (edge.source_gene_id, edge.target_gene_id): edge
            for edge in parent_a.edges
            if edge.source_gene_id in inherited_gene_ids
            and edge.target_gene_id in inherited_gene_ids
        }

        b_edges = {
            (edge.source_gene_id, edge.target_gene_id): edge
            for edge in parent_b.edges
            if edge.source_gene_id in inherited_gene_ids
            and edge.target_gene_id in inherited_gene_ids
        }

        all_keys = set(a_edges.keys()) | set(b_edges.keys())
        child_edges: list[GeneEdge] = []

        for key in all_keys:
            edge_a = a_edges.get(key)
            edge_b = b_edges.get(key)

            if edge_a is not None and edge_b is not None:
                if rng.random() <= self.inherit_shared_edges_probability:
                    child_edges.append(self._merge_shared_edges(edge_a, edge_b, rng))
                continue

            if edge_a is not None:
                if rng.random() <= self.inherit_unique_edge_probability:
                    child_edges.append(edge_a)
                continue

            if edge_b is not None:
                if rng.random() <= self.inherit_unique_edge_probability:
                    child_edges.append(edge_b)

        return child_edges

    def _merge_shared_edges(
        self,
        edge_a: GeneEdge,
        edge_b: GeneEdge,
        rng: random.Random,
    ) -> GeneEdge:
        """
        Если одно и то же ребро есть у обоих родителей,
        можно:
        - выбрать вес одного из родителей
        - или усреднить
        """
        merged_weight = (edge_a.weight + edge_b.weight) / 2.0

        return GeneEdge(
            source_gene_id=edge_a.source_gene_id,
            target_gene_id=edge_a.target_gene_id,
            weight=merged_weight,
        )
