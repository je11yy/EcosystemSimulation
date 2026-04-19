from dataclasses import dataclass
from random import Random
from typing import Dict, Optional, Set, Tuple

from .compatibility import GenomeCompatibilityCalculator
from .effect_type import GeneEffectType
from .models import Gene, Genome
from .mutation import GenomeMutationResult, GenomeMutator


@dataclass(frozen=True)
class GenomeRecombinationConfig:
    # Вероятность брать среднее значение признака у двух гомологичных генов.
    # Если усреднение не сработало, параметр берется от одного из родителей.
    blend_gene_parameters_rate: float = 0.35

    # Уникальные гены одного родителя иногда наследуются ребенком как
    # структурная вариация.
    unique_gene_inheritance_rate: float = 0.25

    # Уникальные ребра одного родителя наследуются не всегда: связи в графе
    # считаем более хрупкими, чем сами гены.
    unique_edge_inheritance_rate: float = 0.45

    # Если оба родителя дают одну и ту же связь, ее вес иногда усредняется.
    blend_edge_weight_rate: float = 0.5

    # Мутации после рекомбинации имитируют ошибки копирования и новые варианты.
    apply_mutations: bool = True


@dataclass(frozen=True)
class GenomeRecombinationReport:
    matched_genes: Dict[int, int]
    inherited_from_left: int
    inherited_from_right: int
    blended_genes: int
    inherited_edges: int
    blended_edges: int
    mutation: Optional[GenomeMutationResult] = None


@dataclass(frozen=True)
class GenomeRecombinationResult:
    genome: Genome
    report: GenomeRecombinationReport


class GenomeRecombinator:
    def __init__(
        self,
        config: Optional[GenomeRecombinationConfig] = None,
        compatibility_calculator: Optional[GenomeCompatibilityCalculator] = None,
        mutator: Optional[GenomeMutator] = None,
    ) -> None:
        self.config = config or GenomeRecombinationConfig()
        self.compatibility_calculator = compatibility_calculator or GenomeCompatibilityCalculator()
        self.mutator = mutator or GenomeMutator()

    def recombine(
        self,
        left: Genome,
        right: Genome,
        rng: Optional[Random] = None,
    ) -> GenomeRecombinationResult:
        rng = rng or Random()
        compatibility = self.compatibility_calculator.calculate(left, right)
        matched_genes = compatibility.matched_genes

        child = Genome()
        id_map_left: Dict[int, int] = {}
        id_map_right: Dict[int, int] = {}
        inherited_from_left = 0
        inherited_from_right = 0
        blended_genes = 0

        for left_id, right_id in matched_genes.items():
            child_gene_id = _next_gene_id(child)
            gene, is_blended, source = self._recombine_matched_gene(
                child_gene_id,
                left.genes[left_id],
                right.genes[right_id],
                rng,
            )
            child.add_gene(gene)
            id_map_left[left_id] = child_gene_id
            id_map_right[right_id] = child_gene_id

            if is_blended:
                blended_genes += 1
            elif source == "left":
                inherited_from_left += 1
            else:
                inherited_from_right += 1

        inherited_from_left += self._inherit_unique_genes(
            parent=left,
            child=child,
            id_map=id_map_left,
            excluded_gene_ids=set(matched_genes),
            rng=rng,
        )
        inherited_from_right += self._inherit_unique_genes(
            parent=right,
            child=child,
            id_map=id_map_right,
            excluded_gene_ids=set(matched_genes.values()),
            rng=rng,
        )

        inherited_edges, blended_edges = self._inherit_edges(
            child,
            left,
            right,
            id_map_left,
            id_map_right,
            rng,
        )

        mutation_result = None
        result_genome = child
        if self.config.apply_mutations:
            mutation_result = self.mutator.mutate(
                child,
                rng,
                rate_multiplier=_mutation_rate_multiplier(left, right),
            )
            result_genome = mutation_result.genome

        return GenomeRecombinationResult(
            genome=result_genome,
            report=GenomeRecombinationReport(
                matched_genes=matched_genes,
                inherited_from_left=inherited_from_left,
                inherited_from_right=inherited_from_right,
                blended_genes=blended_genes,
                inherited_edges=inherited_edges,
                blended_edges=blended_edges,
                mutation=mutation_result,
            ),
        )

    def _recombine_matched_gene(
        self,
        child_gene_id: int,
        left: Gene,
        right: Gene,
        rng: Random,
    ) -> Tuple[Gene, bool, str]:
        if rng.random() < self.config.blend_gene_parameters_rate:
            return (
                Gene(
                    id=child_gene_id,
                    name=_combined_gene_name(left, right),
                    effect_type=left.effect_type,
                    threshold=(left.threshold + right.threshold) / 2,
                    weight=(left.weight + right.weight) / 2,
                    default_active=rng.choice([left.default_active, right.default_active]),
                    is_active=False,
                ),
                True,
                "blend",
            )

        source_gene = rng.choice([left, right])
        source = "left"
        if source_gene is right:
            source = "right"

        return (
            _copy_gene(source_gene, child_gene_id),
            False,
            source,
        )

    def _inherit_unique_genes(
        self,
        parent: Genome,
        child: Genome,
        id_map: Dict[int, int],
        excluded_gene_ids: Set[int],
        rng: Random,
    ) -> int:
        inherited = 0
        for gene in parent.genes.values():
            if gene.id in excluded_gene_ids:
                continue
            if rng.random() > self.config.unique_gene_inheritance_rate:
                continue

            child_gene_id = _next_gene_id(child)
            child.add_gene(_copy_gene(gene, child_gene_id))
            id_map[gene.id] = child_gene_id
            inherited += 1

        return inherited

    def _inherit_edges(
        self,
        child: Genome,
        left: Genome,
        right: Genome,
        id_map_left: Dict[int, int],
        id_map_right: Dict[int, int],
        rng: Random,
    ) -> Tuple[int, int]:
        inherited_edges = 0
        blended_edges = 0
        edge_weights: Dict[Tuple[int, int], float] = {}

        left_inherited, left_blended = self._collect_parent_edges(
            edge_weights,
            left,
            id_map_left,
            rng,
        )
        inherited_edges += left_inherited
        blended_edges += left_blended

        right_inherited, right_blended = self._collect_parent_edges(
            edge_weights,
            right,
            id_map_right,
            rng,
        )
        inherited_edges += right_inherited
        blended_edges += right_blended

        for (source_id, target_id), weight in edge_weights.items():
            if source_id == target_id:
                continue
            child.add_edge(source_id, target_id, weight)

        return inherited_edges, blended_edges

    def _collect_parent_edges(
        self,
        edge_weights: Dict[Tuple[int, int], float],
        parent: Genome,
        id_map: Dict[int, int],
        rng: Random,
    ) -> Tuple[int, int]:
        inherited = 0
        blended = 0

        for edge in parent.graph.edges.values():
            child_source_id = id_map.get(edge.source_id)
            child_target_id = id_map.get(edge.target_id)
            if child_source_id is None or child_target_id is None:
                continue

            key = (child_source_id, child_target_id)
            if key in edge_weights:
                edge_weights[key] = self._recombine_edge_weight(
                    edge_weights[key],
                    edge.weight,
                    rng,
                )
                blended += 1
                continue

            if rng.random() > self.config.unique_edge_inheritance_rate:
                continue

            edge_weights[key] = edge.weight
            inherited += 1

        return inherited, blended

    def _recombine_edge_weight(
        self,
        left_weight: float,
        right_weight: float,
        rng: Random,
    ) -> float:
        if rng.random() < self.config.blend_edge_weight_rate:
            return (left_weight + right_weight) / 2
        return rng.choice([left_weight, right_weight])


def _copy_gene(gene: Gene, gene_id: int) -> Gene:
    return Gene(
        id=gene_id,
        name=gene.name,
        effect_type=gene.effect_type,
        threshold=gene.threshold,
        weight=gene.weight,
        default_active=gene.default_active,
        is_active=False,
    )


def _mutation_rate_multiplier(left: Genome, right: Genome) -> float:
    weights = [
        gene.weight
        for genome in (left, right)
        for gene in genome.genes.values()
        if gene.is_active and gene.effect_type == GeneEffectType.MUTATION_RATE
    ]
    if not weights:
        return 1.0
    return max(0.0, sum(weights) / len(weights))


def _combined_gene_name(left: Gene, right: Gene) -> str:
    if left.name == right.name:
        return left.name
    return f"{left.name} / {right.name}"


def _next_gene_id(genome: Genome) -> int:
    if not genome.genes:
        return 1
    return max(genome.genes) + 1
