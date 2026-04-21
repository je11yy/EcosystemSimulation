from dataclasses import dataclass
from random import Random
from typing import Dict, Optional, Set, Tuple

from .compatibility import GenomeCompatibilityCalculator
from .effect_type import GeneEffectType
from .models import Gene, Genome
from .mutation import GenomeMutationResult, GenomeMutator

MAX_GENERATED_GENE_NAME_LENGTH = 120


@dataclass(frozen=True)
class GenomeRecombinationConfig:
    # При совпадении гомологичных генов чаще делаем мягкое смешивание, но
    # итоговое значение держим ближе к материнскому шаблону.
    blend_gene_parameters_rate: float = 0.55

    # Даже без смешивания чаще выбираем материнский вариант гена.
    maternal_gene_selection_bias: float = 0.75

    # Материнские уникальные гены считаем частью обязательного каркаса.
    maternal_unique_gene_inheritance_rate: float = 1.0

    # Отцовские уникальные гены добавляем редко, чтобы не ломать форму графа.
    paternal_unique_gene_inheritance_rate: float = 0.12

    # Материнские ребра образуют базовую регуляторную структуру.
    maternal_edge_inheritance_rate: float = 1.0

    # Уникальные отцовские ребра наследуются с низкой вероятностью.
    paternal_unique_edge_inheritance_rate: float = 0.1

    # Если оба родителя дают одну и ту же связь, иногда усредняем вес, но
    # оставляем значение ближе к материнскому.
    blend_edge_weight_rate: float = 0.5

    # Вес материнского графа при смешивании параметров.
    maternal_parameter_weight: float = 0.7

    # Максимальная допустимая дистанция ребенка от матери по метрике
    # GenomeCompatibilityCalculator.
    max_distance_from_mother: float = 0.3

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
        # В engine left уже передается как мать, right как отец.
        mother = left
        father = right
        rng = rng or Random()
        compatibility = self.compatibility_calculator.calculate(mother, father)
        matched_genes = compatibility.matched_genes

        child = Genome()
        mother_gene_map: Dict[int, int] = {}
        father_gene_map: Dict[int, int] = {}
        inherited_from_left = 0
        inherited_from_right = 0
        blended_genes = 0

        for mother_id, father_id in matched_genes.items():
            child_gene_id = _next_gene_id(child)
            gene, is_blended, source = self._recombine_matched_gene(
                child_gene_id,
                mother.genes[mother_id],
                father.genes[father_id],
                rng,
            )
            child.add_gene(gene)
            mother_gene_map[mother_id] = child_gene_id
            father_gene_map[father_id] = child_gene_id

            if is_blended:
                blended_genes += 1
            elif source == "left":
                inherited_from_left += 1
            else:
                inherited_from_right += 1

        inherited_from_left += self._inherit_unique_genes(
            parent=mother,
            child=child,
            id_map=mother_gene_map,
            excluded_gene_ids=set(matched_genes),
            inheritance_rate=self.config.maternal_unique_gene_inheritance_rate,
            rng=rng,
        )
        inherited_from_right += self._inherit_unique_genes(
            parent=father,
            child=child,
            id_map=father_gene_map,
            excluded_gene_ids=set(matched_genes.values()),
            inheritance_rate=self.config.paternal_unique_gene_inheritance_rate,
            rng=rng,
        )

        self._ensure_non_empty_genome(
            child=child,
            mother=mother,
            father=father,
            mother_gene_map=mother_gene_map,
            father_gene_map=father_gene_map,
            rng=rng,
        )

        inherited_edges, blended_edges = self._inherit_edges(
            child=child,
            mother=mother,
            father=father,
            mother_gene_map=mother_gene_map,
            father_gene_map=father_gene_map,
            rng=rng,
        )

        self._stabilize_child_structure(
            child=child,
            mother=mother,
            father=father,
            father_gene_map=father_gene_map,
        )

        mutation_result = None
        result_genome = child
        if self.config.apply_mutations:
            mutation_result = self.mutator.mutate(
                child,
                rng,
                rate_multiplier=_mutation_rate_multiplier(mother, father),
            )
            result_genome = mutation_result.genome
            self._stabilize_child_structure(
                child=result_genome,
                mother=mother,
                father=father,
                father_gene_map=father_gene_map,
            )

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
        mother: Gene,
        father: Gene,
        rng: Random,
    ) -> Tuple[Gene, bool, str]:
        if rng.random() < self.config.blend_gene_parameters_rate:
            return (
                Gene(
                    id=child_gene_id,
                    name=_combined_gene_name(mother, father),
                    effect_type=mother.effect_type,
                    x=_blend_toward_template(
                        mother.x,
                        father.x,
                        self.config.maternal_parameter_weight,
                    ),
                    y=_blend_toward_template(
                        mother.y,
                        father.y,
                        self.config.maternal_parameter_weight,
                    ),
                    threshold=_blend_toward_template(
                        mother.threshold,
                        father.threshold,
                        self.config.maternal_parameter_weight,
                    ),
                    weight=_blend_toward_template(
                        mother.weight,
                        father.weight,
                        self.config.maternal_parameter_weight,
                    ),
                    default_active=mother.default_active
                    if rng.random() < self.config.maternal_gene_selection_bias
                    else father.default_active,
                    is_active=False,
                ),
                True,
                "blend",
            )

        if rng.random() < self.config.maternal_gene_selection_bias:
            return (_copy_gene(mother, child_gene_id), False, "left")
        return (_copy_gene(father, child_gene_id), False, "right")

    def _inherit_unique_genes(
        self,
        parent: Genome,
        child: Genome,
        id_map: Dict[int, int],
        excluded_gene_ids: Set[int],
        inheritance_rate: float,
        rng: Random,
    ) -> int:
        inherited = 0
        for gene in parent.genes.values():
            if gene.id in excluded_gene_ids:
                continue
            if rng.random() > inheritance_rate:
                continue

            child_gene_id = _next_gene_id(child)
            child.add_gene(_copy_gene(gene, child_gene_id))
            id_map[gene.id] = child_gene_id
            inherited += 1

        return inherited

    def _ensure_non_empty_genome(
        self,
        child: Genome,
        mother: Genome,
        father: Genome,
        mother_gene_map: Dict[int, int],
        father_gene_map: Dict[int, int],
        rng: Random,
    ) -> None:
        if child.genes:
            return

        fallback_parent = mother if mother.genes else father
        fallback_map = mother_gene_map if fallback_parent is mother else father_gene_map
        if not fallback_parent.genes:
            return

        source_gene = rng.choice(list(fallback_parent.genes.values()))
        child_gene_id = _next_gene_id(child)
        child.add_gene(_copy_gene(source_gene, child_gene_id))
        fallback_map[source_gene.id] = child_gene_id

    def _inherit_edges(
        self,
        child: Genome,
        mother: Genome,
        father: Genome,
        mother_gene_map: Dict[int, int],
        father_gene_map: Dict[int, int],
        rng: Random,
    ) -> Tuple[int, int]:
        inherited_edges = 0
        blended_edges = 0
        edge_weights: Dict[Tuple[int, int], float] = {}

        mother_inherited, mother_blended = self._collect_parent_edges(
            edge_weights=edge_weights,
            parent=mother,
            id_map=mother_gene_map,
            inheritance_rate=self.config.maternal_edge_inheritance_rate,
            rng=rng,
        )
        inherited_edges += mother_inherited
        blended_edges += mother_blended

        father_inherited, father_blended = self._collect_parent_edges(
            edge_weights=edge_weights,
            parent=father,
            id_map=father_gene_map,
            inheritance_rate=self.config.paternal_unique_edge_inheritance_rate,
            rng=rng,
        )
        inherited_edges += father_inherited
        blended_edges += father_blended

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
        inheritance_rate: float,
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

            if rng.random() > inheritance_rate:
                continue

            edge_weights[key] = edge.weight
            inherited += 1

        return inherited, blended

    def _recombine_edge_weight(
        self,
        mother_weight: float,
        father_weight: float,
        rng: Random,
    ) -> float:
        if rng.random() < self.config.blend_edge_weight_rate:
            return _blend_toward_template(
                mother_weight,
                father_weight,
                self.config.maternal_parameter_weight,
            )
        if rng.random() < self.config.maternal_gene_selection_bias:
            return mother_weight
        return father_weight

    def _stabilize_child_structure(
        self,
        child: Genome,
        mother: Genome,
        father: Genome,
        father_gene_map: Dict[int, int],
    ) -> None:
        self._pull_parameters_toward_mother(child, mother)
        self._prune_non_maternal_edges(child, mother)

        if self.compatibility_calculator.calculate(mother, child).distance <= (
            self.config.max_distance_from_mother
        ):
            return

        removable_gene_ids = [
            child_gene_id
            for father_gene_id, child_gene_id in father_gene_map.items()
            if father_gene_id not in mother.genes and child_gene_id in child.genes
        ]
        for child_gene_id in reversed(removable_gene_ids):
            self._remove_gene(child, child_gene_id)
            self._pull_parameters_toward_mother(child, mother)
            self._prune_non_maternal_edges(child, mother)
            if self.compatibility_calculator.calculate(mother, child).distance <= (
                self.config.max_distance_from_mother
            ):
                break

        # В крайнем случае дополнительно откатываем параметры к материнским.
        if self.compatibility_calculator.calculate(mother, child).distance > (
            self.config.max_distance_from_mother
        ):
            self._force_maternal_parameters(child, mother)
            self._prune_non_maternal_edges(child, mother)

        # Защита от вырождения при агрессивной стабилизации.
        if not child.genes and mother.genes:
            mother_gene = next(iter(mother.genes.values()))
            child.add_gene(_copy_gene(mother_gene, _next_gene_id(child)))

        child._sync_edges_from_graph()

    def _pull_parameters_toward_mother(self, child: Genome, mother: Genome) -> None:
        maternal_by_effect = {gene.effect_type: gene for gene in mother.genes.values()}
        for gene_id, gene in list(child.genes.items()):
            mother_gene = maternal_by_effect.get(gene.effect_type)
            if mother_gene is None:
                continue
            child.genes[gene_id] = Gene(
                id=gene.id,
                name=gene.name,
                effect_type=gene.effect_type,
                x=_blend_toward_template(
                    mother_gene.x,
                    gene.x,
                    self.config.maternal_parameter_weight,
                ),
                y=_blend_toward_template(
                    mother_gene.y,
                    gene.y,
                    self.config.maternal_parameter_weight,
                ),
                threshold=_blend_toward_template(
                    mother_gene.threshold,
                    gene.threshold,
                    self.config.maternal_parameter_weight,
                ),
                weight=_blend_toward_template(
                    mother_gene.weight,
                    gene.weight,
                    self.config.maternal_parameter_weight,
                ),
                default_active=mother_gene.default_active
                if self.config.maternal_gene_selection_bias >= 0.5
                else gene.default_active,
                is_active=False,
            )

    def _force_maternal_parameters(self, child: Genome, mother: Genome) -> None:
        maternal_by_effect = {gene.effect_type: gene for gene in mother.genes.values()}
        for gene_id, gene in list(child.genes.items()):
            mother_gene = maternal_by_effect.get(gene.effect_type)
            if mother_gene is None:
                continue
            child.genes[gene_id] = Gene(
                id=gene.id,
                name=gene.name,
                effect_type=gene.effect_type,
                x=mother_gene.x,
                y=mother_gene.y,
                threshold=mother_gene.threshold,
                weight=mother_gene.weight,
                default_active=mother_gene.default_active,
                is_active=False,
            )

    def _prune_non_maternal_edges(self, child: Genome, mother: Genome) -> None:
        maternal_effect_pairs = {
            (
                mother.genes[edge.source_id].effect_type,
                mother.genes[edge.target_id].effect_type,
            )
            for edge in mother.graph.edges.values()
            if edge.source_id in mother.genes and edge.target_id in mother.genes
        }

        child.graph.edges = {
            key: edge
            for key, edge in child.graph.edges.items()
            if self._edge_matches_maternal_pattern(child, edge, maternal_effect_pairs)
        }
        _rebuild_outgoing(child)
        child._sync_edges_from_graph()

    def _edge_matches_maternal_pattern(
        self,
        child: Genome,
        edge,
        maternal_effect_pairs: Set[Tuple[GeneEffectType, GeneEffectType]],
    ) -> bool:
        source_gene = child.genes.get(edge.source_id)
        target_gene = child.genes.get(edge.target_id)
        if source_gene is None or target_gene is None:
            return False
        return (source_gene.effect_type, target_gene.effect_type) in maternal_effect_pairs

    def _remove_gene(self, child: Genome, gene_id: int) -> None:
        if gene_id not in child.genes:
            return
        del child.genes[gene_id]
        child.graph.nodes.discard(gene_id)
        child.graph.outgoing.pop(gene_id, None)
        child.graph.edges = {
            key: edge
            for key, edge in child.graph.edges.items()
            if edge.source_id != gene_id and edge.target_id != gene_id
        }
        _rebuild_outgoing(child)
        child._sync_edges_from_graph()


def _copy_gene(gene: Gene, gene_id: int) -> Gene:
    return Gene(
        id=gene_id,
        name=gene.name,
        effect_type=gene.effect_type,
        x=gene.x,
        y=gene.y,
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
    combined = f"{left.name} / {right.name}"
    if len(combined) <= MAX_GENERATED_GENE_NAME_LENGTH:
        return combined
    truncated = combined[: MAX_GENERATED_GENE_NAME_LENGTH - 3].rstrip()
    return truncated + "..."


def _next_gene_id(genome: Genome) -> int:
    if not genome.genes:
        return 1
    return max(genome.genes) + 1


def _blend_toward_template(
    template_value: float,
    variant_value: float,
    template_weight: float,
) -> float:
    template_weight = max(0.0, min(1.0, template_weight))
    return template_value * template_weight + variant_value * (1.0 - template_weight)


def _rebuild_outgoing(genome: Genome) -> None:
    genome.graph.outgoing = {gene_id: [] for gene_id in genome.graph.nodes}
    for edge in genome.graph.edges.values():
        genome.graph.outgoing.setdefault(edge.source_id, []).append(edge)
