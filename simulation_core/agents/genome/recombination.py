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

    ВАЖНО:
    Сопоставление локусов идёт НЕ по gene.id, а по структурной позиции гена
    на хромосоме: effect_type + chromosome_id + position.
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

        chromosome_ids = sorted(set(parent_a.chromosome_ids()) | set(parent_b.chromosome_ids()))
        next_gene_id = 1

        locus_id_map: dict[tuple, str] = {}

        for chromosome_id in chromosome_ids:
            a_genes = parent_a.genes_on_chromosome(chromosome_id)
            b_genes = parent_b.genes_on_chromosome(chromosome_id)

            if not a_genes and not b_genes:
                continue

            if len(a_genes) != len(b_genes):
                raise ValueError(
                    f"Chromosome '{chromosome_id}' has different gene counts in parents"
                )

            a_loci = [self._gene_locus_key(gene) for gene in a_genes]
            b_loci = [self._gene_locus_key(gene) for gene in b_genes]

            if a_loci != b_loci:
                raise ValueError(
                    f"Chromosome '{chromosome_id}' has different locus order in parents"
                )

            inherited_genes = self._recombine_chromosome(
                genes_a=a_genes,
                genes_b=b_genes,
                rng=rng,
                next_gene_id=next_gene_id,
            )

            for locus_key, gene in inherited_genes:
                child.add_gene(gene)
                locus_id_map[locus_key] = str(gene.id)
                next_gene_id += 1

        inherited_edges = self._inherit_edges(
            parent_a=parent_a,
            parent_b=parent_b,
            locus_id_map=locus_id_map,
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
        next_gene_id: int,
    ) -> list[tuple[tuple, Gene]]:
        if len(genes_a) != len(genes_b):
            raise ValueError("Parents must have the same number of genes on chromosome")

        n = len(genes_a)

        if n == 0:
            return []

        if n == 1:
            chosen = rng.choice([genes_a[0], genes_b[0]])
            locus_key = self._gene_locus_key(chosen)
            return [(locus_key, self._clone_gene_with_new_id(chosen, next_gene_id))]

        start_with_a = rng.choice([True, False])
        crossover_index = rng.randint(1, n - 1)

        child_genes: list[tuple[tuple, Gene]] = []

        current_gene_id = next_gene_id

        for idx in range(n):
            if idx < crossover_index:
                chosen_gene = genes_a[idx] if start_with_a else genes_b[idx]
            else:
                chosen_gene = genes_b[idx] if start_with_a else genes_a[idx]

            locus_key = self._gene_locus_key(chosen_gene)
            cloned_gene = self._clone_gene_with_new_id(chosen_gene, current_gene_id)
            child_genes.append((locus_key, cloned_gene))
            current_gene_id += 1

        return child_genes

    def _inherit_edges(
        self,
        parent_a: Genome,
        parent_b: Genome,
        locus_id_map: dict[tuple, str],
        rng: random.Random,
    ) -> list[GeneEdge]:
        a_edges = self._edge_map_by_locus(parent_a)
        b_edges = self._edge_map_by_locus(parent_b)

        all_keys = set(a_edges.keys()) | set(b_edges.keys())
        child_edges: list[GeneEdge] = []

        for key in all_keys:
            edge_a = a_edges.get(key)
            edge_b = b_edges.get(key)

            source_locus, target_locus = key
            child_source_id = locus_id_map.get(source_locus)
            child_target_id = locus_id_map.get(target_locus)

            if child_source_id is None or child_target_id is None:
                continue

            if edge_a is not None and edge_b is not None:
                if rng.random() <= self.inherit_shared_edges_probability:
                    merged_weight = (edge_a.weight + edge_b.weight) / 2.0
                    child_edges.append(
                        GeneEdge(
                            source_gene_id=child_source_id,
                            target_gene_id=child_target_id,
                            weight=merged_weight,
                        )
                    )
                continue

            if edge_a is not None:
                if rng.random() <= self.inherit_unique_edge_probability:
                    child_edges.append(
                        GeneEdge(
                            source_gene_id=child_source_id,
                            target_gene_id=child_target_id,
                            weight=edge_a.weight,
                        )
                    )
                continue

            if edge_b is not None:
                if rng.random() <= self.inherit_unique_edge_probability:
                    child_edges.append(
                        GeneEdge(
                            source_gene_id=str(child_source_id),
                            target_gene_id=str(child_target_id),
                            weight=edge_b.weight,
                        )
                    )

        return child_edges

    def _edge_map_by_locus(self, genome: Genome) -> dict[tuple[tuple, tuple], GeneEdge]:
        result: dict[tuple[tuple, tuple], GeneEdge] = {}

        for edge in genome.edges:
            source_gene = genome.get_gene(edge.source_gene_id)
            target_gene = genome.get_gene(edge.target_gene_id)

            key = (
                self._gene_locus_key(source_gene),
                self._gene_locus_key(target_gene),
            )
            result[key] = edge

        return result

    def _gene_locus_key(self, gene: Gene) -> tuple:
        return (
            gene.effect_type.value,
            gene.chromosome_id,
            round(gene.position, 6),
        )

    def _clone_gene_with_new_id(self, gene: Gene, new_id: int) -> Gene:
        return Gene(
            id=str(new_id),
            name=gene.name,
            effect_type=gene.effect_type,
            chromosome_id=gene.chromosome_id,
            position=gene.position,
            default_active=gene.default_active,
            threshold=gene.threshold,
        )
