from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .models import Gene, Genome


@dataclass(frozen=True)
class GeneCompatibilityWeights:
    # Разные типы эффекта считаются разными функциональными ролями гена.
    effect_type_mismatch: float = 1.0

    # Порог важен, но обычно небольшая мутация порога не должна резко ломать
    # совместимость.
    threshold: float = 0.2

    # Сила гена сильнее влияет на фенотип и поведение, поэтому она тяжелее
    # порога.
    weight: float = 0.6

    # default_active меняет режим включения гена, но сам эффект остается тем же.
    default_active: float = 0.2


@dataclass(frozen=True)
class GenomeCompatibilityWeights:
    # Вершины важнее всего: если состав генов сильно разный, похожая топология
    # уже не так много значит.
    genes: float = 0.55

    # Ребра описывают регуляторную структуру между генами.
    edges: float = 0.35

    # Топология дает мягкий штраф за различия формы графа: плотность связей,
    # входящие и исходящие степени.
    topology: float = 0.1

    gene: GeneCompatibilityWeights = field(default_factory=GeneCompatibilityWeights)


@dataclass(frozen=True)
class GenomeCompatibility:
    score: float
    distance: float
    gene_distance: float
    edge_distance: float
    topology_distance: float
    matched_genes: Dict[int, int]

    @property
    def is_identical(self) -> bool:
        return self.distance == 0.0


class GenomeCompatibilityCalculator:
    def __init__(
        self,
        weights: Optional[GenomeCompatibilityWeights] = None,
    ) -> None:
        self.weights = weights or GenomeCompatibilityWeights()

    def calculate(self, left: Genome, right: Genome) -> GenomeCompatibility:
        matched_genes, gene_distance = self._match_genes(left, right)
        edge_distance = self._calculate_edge_distance(left, right, matched_genes)
        topology_distance = self._calculate_topology_distance(left, right)

        distance = _clamp01(
            self.weights.genes * gene_distance
            + self.weights.edges * edge_distance
            + self.weights.topology * topology_distance
        )

        return GenomeCompatibility(
            score=1.0 - distance,
            distance=distance,
            gene_distance=gene_distance,
            edge_distance=edge_distance,
            topology_distance=topology_distance,
            matched_genes=matched_genes,
        )

    def is_compatible(
        self,
        left: Genome,
        right: Genome,
        min_score: float = 0.65,
    ) -> bool:
        return self.calculate(left, right).score >= min_score

    def _match_genes(self, left: Genome, right: Genome) -> Tuple[Dict[int, int], float]:
        if not left.genes and not right.genes:
            return {}, 0.0

        candidates = []
        for left_gene in left.genes.values():
            for right_gene in right.genes.values():
                candidates.append(
                    (
                        self._calculate_gene_distance(left_gene, right_gene),
                        left_gene.id,
                        right_gene.id,
                    )
                )

        candidates.sort()

        matched_left: Set[int] = set()
        matched_right: Set[int] = set()
        matched_genes: Dict[int, int] = {}
        matched_distance = 0.0

        for distance, left_id, right_id in candidates:
            if distance >= 1.0:
                continue
            if left_id in matched_left or right_id in matched_right:
                continue

            matched_left.add(left_id)
            matched_right.add(right_id)
            matched_genes[left_id] = right_id
            matched_distance += distance

        unmatched_count = (
            len(left.genes) - len(matched_left) + len(right.genes) - len(matched_right)
        )
        denominator = max(len(left.genes), len(right.genes), 1)
        gene_distance = (matched_distance + unmatched_count) / denominator

        return matched_genes, _clamp01(gene_distance)

    def _calculate_gene_distance(self, left: Gene, right: Gene) -> float:
        if left.effect_type != right.effect_type:
            return self.weights.gene.effect_type_mismatch

        default_active_distance = 0.0
        if left.default_active != right.default_active:
            default_active_distance = 1.0

        return _clamp01(
            self.weights.gene.threshold * _normalized_delta(left.threshold, right.threshold)
            + self.weights.gene.weight * _normalized_delta(left.weight, right.weight)
            + self.weights.gene.default_active * default_active_distance
        )

    def _calculate_edge_distance(
        self,
        left: Genome,
        right: Genome,
        matched_genes: Dict[int, int],
    ) -> float:
        if not left.graph.edges and not right.graph.edges:
            return 0.0

        matched_right_edges = set()
        distance = 0.0

        for left_edge in left.graph.edges.values():
            right_source_id = matched_genes.get(left_edge.source_id)
            right_target_id = matched_genes.get(left_edge.target_id)

            if right_source_id is None or right_target_id is None:
                distance += 1.0
                continue

            right_edge = right.graph.get_edge(right_source_id, right_target_id)
            if right_edge is None:
                distance += 1.0
                continue

            matched_right_edges.add(right_edge.key)
            distance += _normalized_delta(left_edge.weight, right_edge.weight)

        distance += len(right.graph.edges) - len(matched_right_edges)
        denominator = max(len(left.graph.edges), len(right.graph.edges), 1)

        return _clamp01(distance / denominator)

    def _calculate_topology_distance(self, left: Genome, right: Genome) -> float:
        node_count_distance = _count_distance(len(left.genes), len(right.genes))
        edge_count_distance = _count_distance(
            len(left.graph.edges),
            len(right.graph.edges),
        )
        degree_distance = _degree_profile_distance(left, right)

        return _clamp01(
            0.35 * node_count_distance + 0.35 * edge_count_distance + 0.3 * degree_distance
        )


def _degree_profile_distance(left: Genome, right: Genome) -> float:
    left_profile = _degree_profile(left)
    right_profile = _degree_profile(right)
    profile_len = max(len(left_profile), len(right_profile))
    if profile_len == 0:
        return 0.0

    left_profile = _pad_profile(left_profile, profile_len)
    right_profile = _pad_profile(right_profile, profile_len)

    distance = 0.0
    for left_degree, right_degree in zip(left_profile, right_profile):  # noqa: B905
        distance += _count_distance(left_degree, right_degree)

    return _clamp01(distance / profile_len)


def _degree_profile(genome: Genome) -> List[int]:
    degrees = {gene_id: 0 for gene_id in genome.genes}

    for edge in genome.graph.edges.values():
        degrees[edge.source_id] = degrees.get(edge.source_id, 0) + 1
        degrees[edge.target_id] = degrees.get(edge.target_id, 0) + 1

    return sorted(degrees.values(), reverse=True)


def _pad_profile(profile: List[int], length: int) -> List[int]:
    return profile + [0] * (length - len(profile))


def _count_distance(left: int, right: int) -> float:
    return _clamp01(abs(left - right) / max(left, right, 1))


def _normalized_delta(left: float, right: float) -> float:
    return _clamp01(abs(left - right) / (abs(left) + abs(right) + 1.0))


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
