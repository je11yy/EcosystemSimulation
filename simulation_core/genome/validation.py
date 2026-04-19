from dataclasses import replace
from typing import Optional

from ..agent.observation import Observation
from ..agent.state import AgentState
from .effect_type import GeneEffectType
from .models import Gene, Genome


def validate_genome_for_agent_state(
    genome: Genome,
    state: AgentState,
    observation: Optional[Observation] = None,
) -> Genome:
    return Genome(
        genes={
            gene_id: replace(
                gene,
                is_active=should_activate_gene(gene, state, observation),
            )
            for gene_id, gene in genome.genes.items()
        },
        graph=genome.graph.copy(),
    )


def should_activate_gene(
    gene: Gene,
    state: AgentState,
    observation: Optional[Observation] = None,
) -> bool:
    if gene.default_active:
        return True

    effect_type = GeneEffectType(gene.effect_type)

    # Статовые и метаболические гены описывают базовую физиологию. Они не
    # должны включаться только при кризисном hp или низкой силе агента.
    if effect_type in _CONSTITUTIVE_EFFECTS:
        return True

    if effect_type == GeneEffectType.HUNGER_DRIVE:
        return state.hunger >= gene.threshold

    if effect_type == GeneEffectType.REPRODUCTION_DRIVE:
        return not state.is_pregnant and state.satisfaction >= gene.threshold

    if effect_type == GeneEffectType.DISPERSAL_DRIVE:
        return (
            state.satisfaction <= gene.threshold
            or _local_occupant_count(observation) >= gene.threshold
            or _temperature_discomfort(state, observation) >= gene.threshold
        )

    if effect_type == GeneEffectType.SITE_FIDELITY:
        return (
            state.satisfaction >= gene.threshold
            and _temperature_discomfort(state, observation) <= gene.threshold
        )

    if effect_type == GeneEffectType.HEAT_RESISTANCE:
        temperature = _local_temperature(observation)
        return temperature is not None and temperature >= gene.threshold

    if effect_type == GeneEffectType.COLD_RESISTANCE:
        temperature = _local_temperature(observation)
        return temperature is not None and temperature <= gene.threshold

    if effect_type == GeneEffectType.AGGRESSION_DRIVE:
        return (
            state.hunger >= gene.threshold or _local_occupant_count(observation) >= gene.threshold
        )

    if effect_type == GeneEffectType.PREDATION_DRIVE:
        return state.hunger >= gene.threshold and _visible_agent_count(observation) > 0

    if effect_type == GeneEffectType.CARNIVORE_DIGESTION:
        return state.hunger >= gene.threshold

    if effect_type == GeneEffectType.CANNIBAL_TOLERANCE:
        return state.hunger >= gene.threshold and _visible_agent_count(observation) > 0

    if effect_type == GeneEffectType.SOCIAL_TOLERANCE:
        return _local_occupant_count(observation) >= gene.threshold

    return False


_CONSTITUTIVE_EFFECTS = {
    GeneEffectType.MAX_HP,
    GeneEffectType.STRENGTH,
    GeneEffectType.DEFENSE,
    GeneEffectType.METABOLISM,
}


def _local_temperature(observation: Optional[Observation]) -> Optional[float]:
    if observation is None:
        return None
    return observation.current_territory.temperature


def _local_occupant_count(observation: Optional[Observation]) -> float:
    if observation is None:
        return 0.0
    return observation.current_territory.occupant_count


def _visible_agent_count(observation: Optional[Observation]) -> int:
    if observation is None:
        return 0
    return len(observation.agents)


def _temperature_discomfort(
    state: AgentState,
    observation: Optional[Observation],
) -> float:
    temperature = _local_temperature(observation)
    if temperature is None:
        return 0.0
    return abs(temperature - state.base_temp_pref)
