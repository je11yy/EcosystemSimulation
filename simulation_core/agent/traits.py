from dataclasses import dataclass

from ..genome.effect_type import GeneEffectType
from ..genome.models import Gene, Genome


@dataclass(frozen=True)
class TraitVector:
    metabolism: float = 1.0
    hunger_drive: float = 1.0
    dispersal_drive: float = 1.0
    site_fidelity: float = 1.0
    reproduction_drive: float = 1.0
    heat_resistance: float = 0.0
    cold_resistance: float = 0.0
    aggression_drive: float = 1.0
    predation_drive: float = 1.0
    carnivore_digestion: float = 1.0
    cannibal_tolerance: float = 0.0
    social_tolerance: float = 0.0


class TraitAggregator:
    def __init__(self, genome: Genome):
        self.genome = genome
        self.active_genes = [gene for gene in genome.genes.values() if gene.is_active]
        self.weights_by_type = self._group_effective_weights_by_type()

    def build_vector(self) -> TraitVector:
        return TraitVector(
            metabolism=max(0.1, self.multiplier(GeneEffectType.METABOLISM)),
            hunger_drive=self.sum_or_default(GeneEffectType.HUNGER_DRIVE),
            dispersal_drive=self.sum_or_default(GeneEffectType.DISPERSAL_DRIVE),
            site_fidelity=self.sum_or_default(GeneEffectType.SITE_FIDELITY),
            reproduction_drive=self.sum_or_default(GeneEffectType.REPRODUCTION_DRIVE),
            heat_resistance=self.total(GeneEffectType.HEAT_RESISTANCE),
            cold_resistance=self.total(GeneEffectType.COLD_RESISTANCE),
            aggression_drive=self.sum_or_default(GeneEffectType.AGGRESSION_DRIVE),
            predation_drive=self.sum_or_default(GeneEffectType.PREDATION_DRIVE),
            carnivore_digestion=self.sum_or_default(GeneEffectType.CARNIVORE_DIGESTION),
            cannibal_tolerance=self.total(GeneEffectType.CANNIBAL_TOLERANCE),
            social_tolerance=self.total(GeneEffectType.SOCIAL_TOLERANCE),
        )

    def multiplier(self, effect_type: GeneEffectType) -> float:
        result = 1.0
        for weight in self.weights_by_type[effect_type]:
            result *= weight
        return result

    def total(self, effect_type: GeneEffectType) -> float:
        return sum(self.weights_by_type[effect_type])

    def sum_or_default(self, effect_type: GeneEffectType, default: float = 1.0) -> float:
        weights = self.weights_by_type[effect_type]
        if not weights:
            return default
        return sum(weights)

    def _group_effective_weights_by_type(self) -> dict[GeneEffectType, list[float]]:
        active_gene_ids = {gene.id for gene in self.active_genes}
        genes_by_id = {gene.id: gene for gene in self.active_genes}
        weights_by_type = {effect_type: [] for effect_type in GeneEffectType}

        for gene in self.active_genes:
            weights_by_type[GeneEffectType(gene.effect_type)].append(
                self._effective_gene_weight(gene, active_gene_ids, genes_by_id)
            )

        return weights_by_type

    def _effective_gene_weight(
        self,
        gene: Gene,
        active_gene_ids: set[int],
        genes_by_id: dict[int, Gene],
    ) -> float:
        weight = gene.weight
        for edge in self.genome.graph.edges.values():
            if edge.target_id != gene.id or edge.source_id not in active_gene_ids:
                continue
            if edge.source_id not in genes_by_id:
                continue
            weight *= edge.weight
        return weight
