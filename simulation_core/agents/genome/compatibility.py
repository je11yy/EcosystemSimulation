from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from simulation_core.agents.genome.genome import Genome


@dataclass(frozen=True)
class GenomeCompatibilityResult:
    distance: float
    compatible: bool


class GenomeCompatibilityCalculator:
    def __init__(
        self,
        max_distance: float = 0.3,
        vertex_weight: float = 0.35,
        edge_weight: float = 0.35,
        connection_weight_delta_weight: float = 0.15,
        threshold_delta_weight: float = 0.15,
    ) -> None:
        self.max_distance = max_distance
        self.vertex_weight = vertex_weight
        self.edge_weight = edge_weight
        self.connection_weight_delta_weight = connection_weight_delta_weight
        self.threshold_delta_weight = threshold_delta_weight

    def calculate_distance(self, genome_a: Genome, genome_b: Genome) -> float:
        gene_profiles_a = self._gene_profile_counter(genome_a)
        gene_profiles_b = self._gene_profile_counter(genome_b)
        dv = self._multiset_jaccard_distance(gene_profiles_a, gene_profiles_b)

        edge_profiles_a = self._edge_profile_counter(genome_a)
        edge_profiles_b = self._edge_profile_counter(genome_b)
        de = self._multiset_jaccard_distance(edge_profiles_a, edge_profiles_b)

        dw = self._mean_weight_difference(genome_a, genome_b)
        dt = self._mean_threshold_difference(genome_a, genome_b)

        return (
            self.vertex_weight * dv
            + self.edge_weight * de
            + self.connection_weight_delta_weight * dw
            + self.threshold_delta_weight * dt
        )

    def check(self, genome_a: Genome, genome_b: Genome) -> GenomeCompatibilityResult:
        distance = self.calculate_distance(genome_a, genome_b)
        return GenomeCompatibilityResult(
            distance=distance,
            compatible=distance <= self.max_distance,
        )

    def _gene_profile_counter(self, genome: Genome) -> Counter[tuple]:
        return Counter(
            (
                gene.effect_type,
                gene.chromosome_id,
                round(gene.position, 1),
                gene.default_active,
            )
            for gene in genome.all_genes()
        )

    def _edge_profile_counter(self, genome: Genome) -> Counter[tuple]:
        return Counter(
            (
                genome.get_gene(edge.source_gene_id).effect_type,
                genome.get_gene(edge.target_gene_id).effect_type,
                round(edge.weight, 1),
            )
            for edge in genome.edges
        )

    def _multiset_jaccard_distance(self, a: Counter, b: Counter) -> float:
        keys = set(a) | set(b)
        if not keys:
            return 0.0

        intersection = sum(min(a[key], b[key]) for key in keys)
        union = sum(max(a[key], b[key]) for key in keys)
        return 1.0 - intersection / union

    def _mean_weight_difference(self, genome_a: Genome, genome_b: Genome) -> float:
        edge_map_a = self._edge_weight_profile(genome_a)
        edge_map_b = self._edge_weight_profile(genome_b)

        shared = set(edge_map_a.keys()) & set(edge_map_b.keys())
        if not shared:
            return 0.0

        diffs = [abs(edge_map_a[key] - edge_map_b[key]) for key in shared]
        return min(1.0, sum(diffs) / len(diffs) / 3.0)

    def _edge_weight_profile(self, genome: Genome) -> dict[tuple, float]:
        profile: dict[tuple, float] = {}
        for edge in genome.edges:
            key = (
                genome.get_gene(edge.source_gene_id).effect_type,
                genome.get_gene(edge.target_gene_id).effect_type,
            )
            profile[key] = edge.weight
        return profile

    def _mean_threshold_difference(self, genome_a: Genome, genome_b: Genome) -> float:
        gene_map_a = self._threshold_profile(genome_a)
        gene_map_b = self._threshold_profile(genome_b)

        shared = set(gene_map_a.keys()) & set(gene_map_b.keys())
        if not shared:
            return 0.0

        diffs = [abs(gene_map_a[key] - gene_map_b[key]) for key in shared]
        return min(1.0, sum(diffs) / len(diffs) / 3.0)

    def _threshold_profile(self, genome: Genome) -> dict[tuple, float]:
        profile: dict[tuple, float] = {}
        for gene in genome.all_genes():
            key = (
                gene.effect_type,
                gene.chromosome_id,
                round(gene.position, 1),
            )
            profile[key] = gene.threshold
        return profile
