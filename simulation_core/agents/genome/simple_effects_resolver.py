from dataclasses import dataclass

from simulation_core.agents.genome.effects import GenomeEffects, GenomeEffectsResolver
from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.genome.state import GenomeState


@dataclass(frozen=True)
class SimpleGenomeEffectsResolver(GenomeEffectsResolver):
    """
    Простое правило:
    активные гены дают дельты к базовым характеристикам.
    """

    def resolve(
        self,
        genome: Genome,
        genome_state: GenomeState,
    ) -> GenomeEffects:
        strength_delta = 0
        defense_delta = 0
        temp_pref_delta = 0.0

        if genome_state.is_active("g_hunger_drive"):
            strength_delta += 1

        if genome_state.is_active("g_low_activity"):
            strength_delta -= 1
            defense_delta += 1

        if genome_state.is_active("g_heat_resistance"):
            temp_pref_delta += 3.0

        if genome_state.is_active("g_cold_resistance"):
            temp_pref_delta -= 3.0

        if genome_state.is_active("g_risk_move"):
            strength_delta += 1

        return GenomeEffects(
            strength_delta=strength_delta,
            defense_delta=defense_delta,
            temp_pref_delta=temp_pref_delta,
        )
