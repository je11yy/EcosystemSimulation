from dataclasses import dataclass

from simulation_core.agents.genome import Genome, GenomeState
from simulation_core.agents.genome.effect_type import GeneEffectType
from simulation_core.agents.observation import Observation
from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.state import IndividualState
from simulation_core.config import SimConfig
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class TraitVector:
    feeding_drive: float = 0.0
    food_opportunism: float = 0.0
    activity_level: float = 0.0
    movement_drive: float = 0.0
    risk_taking: float = 0.0
    site_fidelity: float = 0.0
    reproduction_drive: float = 0.0
    mate_selectivity: float = 0.0
    parental_investment: float = 0.0
    heat_resistance: float = 0.0
    cold_resistance: float = 0.0
    habitat_sensitivity: float = 0.0
    defense_drive: float = 0.0
    escape_drive: float = 0.0
    aggression_drive: float = 0.0
    predation_drive: float = 0.0
    carnivore_digestion: float = 0.0
    cannibal_tolerance: float = 0.0
    social_tolerance: float = 0.0
    kin_avoidance: float = 0.0


@dataclass(frozen=True)
class TraitAggregationContext:
    hunger_ratio: float
    local_food_ratio: float
    local_food_scarcity: float
    local_density_ratio: float
    temperature_stress: float
    hunt_cooldown_ratio: float


class TraitAggregator:
    """
    Преобразует активные гены и контекст среды в агрегированный вектор трейтов,
    на который затем может опираться policy.
    """

    def aggregate(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome: Genome,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> TraitVector:
        ctx = self._build_context(
            state=state,
            phenotype=phenotype,
            obs=obs,
            world=world,
            cfg=cfg,
        )

        traits = _MutableTraitVector()
        active_effects = self._active_effect_types(genome=genome, genome_state=genome_state)

        self._apply_base_gene_effects(traits=traits, active_effects=active_effects)
        self._apply_antagonisms(traits=traits, active_effects=active_effects)
        self._apply_dependencies(traits=traits, active_effects=active_effects)
        self._apply_synergies(traits=traits, active_effects=active_effects)
        self._apply_environmental_modulation(
            traits=traits,
            ctx=ctx,
            active_effects=active_effects,
        )

        traits.clamp_min(0.0)
        return traits.freeze()

    def _active_effect_types(
        self,
        genome: Genome,
        genome_state: GenomeState,
    ) -> set[GeneEffectType]:
        active_effects: set[GeneEffectType] = set()

        for gene in genome.all_genes():
            if genome_state.is_active(gene.id):
                active_effects.add(gene.effect_type)

        return active_effects

    def _build_context(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> TraitAggregationContext:
        current = world.get_territory(obs.current_id)
        territories = list(world.all_territories())

        max_food_capacity = max((territory.food_capacity for territory in territories), default=0.0)
        reference_food = max(1.0, max_food_capacity, current.food_capacity)

        hunger_ratio = state.hunger / cfg.hunger_max if cfg.hunger_max > 0 else 0.0
        local_food_ratio = self._clamp01(current.food / reference_food)
        local_food_scarcity = 1.0 - local_food_ratio
        local_density_ratio = self._clamp01(len(obs.individuals_here) / 4.0)

        temperature_gap = abs(current.temperature - phenotype.temp_pref)
        temperature_stress = self._clamp01(temperature_gap / 15.0)

        hunt_cooldown_ratio = self._clamp01(state.hunt_cooldown / 3.0)

        return TraitAggregationContext(
            hunger_ratio=hunger_ratio,
            local_food_ratio=local_food_ratio,
            local_food_scarcity=local_food_scarcity,
            local_density_ratio=local_density_ratio,
            temperature_stress=temperature_stress,
            hunt_cooldown_ratio=hunt_cooldown_ratio,
        )

    def _apply_base_gene_effects(
        self,
        traits: "_MutableTraitVector",
        active_effects: set[GeneEffectType],
    ) -> None:
        if GeneEffectType.HUNGER_DRIVE in active_effects:
            traits.feeding_drive += 1.1

        if GeneEffectType.SMALL_APPETITE in active_effects:
            traits.feeding_drive -= 0.9

        if GeneEffectType.FOOD_OPPORTUNISM in active_effects:
            traits.food_opportunism += 0.9

        if GeneEffectType.LOW_ACTIVITY in active_effects:
            traits.activity_level -= 1.0

        if GeneEffectType.RISK_MOVE in active_effects:
            traits.risk_taking += 0.9

        if GeneEffectType.DISPERSAL_DRIVE in active_effects:
            traits.movement_drive += 1.0

        if GeneEffectType.SITE_FIDELITY in active_effects:
            traits.site_fidelity += 1.0

        if GeneEffectType.REPRODUCTION_DRIVE in active_effects:
            traits.reproduction_drive += 1.0

        if GeneEffectType.MATE_SELECTIVITY in active_effects:
            traits.mate_selectivity += 1.0

        if GeneEffectType.PARENTAL_INVESTMENT in active_effects:
            traits.parental_investment += 1.0

        if GeneEffectType.HEAT_RESISTANCE in active_effects:
            traits.heat_resistance += 1.0

        if GeneEffectType.COLD_RESISTANCE in active_effects:
            traits.cold_resistance += 1.0

        if GeneEffectType.HABITAT_SATISFACTION in active_effects:
            traits.habitat_sensitivity += 1.0

        if GeneEffectType.DEFENSE_RESPONSE in active_effects:
            traits.defense_drive += 1.0

        if GeneEffectType.ESCAPE_RESPONSE in active_effects:
            traits.escape_drive += 1.0

        if GeneEffectType.AGGRESSION_DRIVE in active_effects:
            traits.aggression_drive += 1.0

        if GeneEffectType.PREDATION_DRIVE in active_effects:
            traits.predation_drive += 1.0

        if GeneEffectType.CARNIVORE_DIGESTION in active_effects:
            traits.carnivore_digestion += 1.0

        if GeneEffectType.CANNIBAL_TOLERANCE in active_effects:
            traits.cannibal_tolerance += 1.0

        if GeneEffectType.SOCIAL_TOLERANCE in active_effects:
            traits.social_tolerance += 1.0

        if GeneEffectType.KIN_AVOIDANCE in active_effects:
            traits.kin_avoidance += 1.0

    def _apply_antagonisms(
        self,
        traits: "_MutableTraitVector",
        active_effects: set[GeneEffectType],
    ) -> None:
        if GeneEffectType.LOW_ACTIVITY in active_effects:
            traits.movement_drive -= 0.7
            traits.aggression_drive -= 0.6
            traits.predation_drive -= 0.6

        if GeneEffectType.SITE_FIDELITY in active_effects:
            traits.movement_drive -= 0.5

        if GeneEffectType.ESCAPE_RESPONSE in active_effects:
            traits.aggression_drive -= 0.6

    def _apply_dependencies(
        self,
        traits: "_MutableTraitVector",
        active_effects: set[GeneEffectType],
    ) -> None:
        if GeneEffectType.PREDATION_DRIVE not in active_effects:
            traits.cannibal_tolerance *= 0.15
            traits.carnivore_digestion *= 0.25

        if GeneEffectType.REPRODUCTION_DRIVE not in active_effects:
            traits.mate_selectivity *= 0.15

    def _apply_synergies(
        self,
        traits: "_MutableTraitVector",
        active_effects: set[GeneEffectType],
    ) -> None:
        if {
            GeneEffectType.HUNGER_DRIVE,
            GeneEffectType.FOOD_OPPORTUNISM,
        }.issubset(active_effects):
            traits.feeding_drive += 0.45
            traits.food_opportunism += 0.35

        if {
            GeneEffectType.PREDATION_DRIVE,
            GeneEffectType.AGGRESSION_DRIVE,
        }.issubset(active_effects):
            traits.predation_drive += 0.5
            traits.aggression_drive += 0.35

        if {
            GeneEffectType.DEFENSE_RESPONSE,
            GeneEffectType.ESCAPE_RESPONSE,
        }.issubset(active_effects):
            traits.defense_drive += 0.35
            traits.escape_drive += 0.35

    def _apply_environmental_modulation(
        self,
        traits: "_MutableTraitVector",
        ctx: TraitAggregationContext,
        active_effects: set[GeneEffectType],
    ) -> None:
        traits.feeding_drive += 1.4 * ctx.hunger_ratio
        traits.reproduction_drive -= 1.0 * ctx.hunger_ratio

        traits.food_opportunism += 0.45 * ctx.local_food_ratio
        traits.predation_drive += 0.9 * ctx.local_food_scarcity

        traits.aggression_drive += 0.7 * ctx.local_density_ratio
        traits.movement_drive += 0.5 * ctx.local_density_ratio
        traits.aggression_drive -= 0.6 * traits.social_tolerance * ctx.local_density_ratio

        traits.predation_drive -= 1.2 * ctx.hunt_cooldown_ratio
        traits.aggression_drive -= 0.4 * ctx.hunt_cooldown_ratio

        traits.reproduction_drive -= 0.6 * traits.parental_investment * ctx.hunger_ratio

        if GeneEffectType.HEAT_RESISTANCE in active_effects:
            traits.heat_resistance += 0.8 * ctx.temperature_stress

        if GeneEffectType.COLD_RESISTANCE in active_effects:
            traits.cold_resistance += 0.8 * ctx.temperature_stress

        if GeneEffectType.HABITAT_SATISFACTION in active_effects:
            comfort = 1.0 - ctx.temperature_stress
            traits.habitat_sensitivity += 0.7 * comfort
            traits.movement_drive += 0.6 * ctx.temperature_stress

        if GeneEffectType.HUNGER_DRIVE in active_effects:
            traits.feeding_drive += 0.5 * ctx.hunger_ratio

        if GeneEffectType.SMALL_APPETITE in active_effects:
            traits.feeding_drive -= 0.4 * (1.0 - ctx.hunger_ratio)

    def _clamp01(self, value: float) -> float:
        return max(0.0, min(1.0, value))


class _MutableTraitVector:
    def __init__(self) -> None:
        self.feeding_drive = 0.0
        self.food_opportunism = 0.0
        self.activity_level = 0.0
        self.movement_drive = 0.0
        self.risk_taking = 0.0
        self.site_fidelity = 0.0
        self.reproduction_drive = 0.0
        self.mate_selectivity = 0.0
        self.parental_investment = 0.0
        self.heat_resistance = 0.0
        self.cold_resistance = 0.0
        self.habitat_sensitivity = 0.0
        self.defense_drive = 0.0
        self.escape_drive = 0.0
        self.aggression_drive = 0.0
        self.predation_drive = 0.0
        self.carnivore_digestion = 0.0
        self.cannibal_tolerance = 0.0
        self.social_tolerance = 0.0
        self.kin_avoidance = 0.0

    def clamp_min(self, minimum: float) -> None:
        for field_name, value in vars(self).items():
            if value < minimum:
                setattr(self, field_name, minimum)

    def freeze(self) -> TraitVector:
        return TraitVector(
            feeding_drive=self.feeding_drive,
            food_opportunism=self.food_opportunism,
            activity_level=self.activity_level,
            movement_drive=self.movement_drive,
            risk_taking=self.risk_taking,
            site_fidelity=self.site_fidelity,
            reproduction_drive=self.reproduction_drive,
            mate_selectivity=self.mate_selectivity,
            parental_investment=self.parental_investment,
            heat_resistance=self.heat_resistance,
            cold_resistance=self.cold_resistance,
            habitat_sensitivity=self.habitat_sensitivity,
            defense_drive=self.defense_drive,
            escape_drive=self.escape_drive,
            aggression_drive=self.aggression_drive,
            predation_drive=self.predation_drive,
            carnivore_digestion=self.carnivore_digestion,
            cannibal_tolerance=self.cannibal_tolerance,
            social_tolerance=self.social_tolerance,
            kin_avoidance=self.kin_avoidance,
        )
