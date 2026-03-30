from dataclasses import dataclass

from simulation_core.agents.genome.effect_type import GeneEffectType
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

        for gene in genome.all_genes():
            if not genome_state.is_active(gene.id):
                continue

            if gene.effect_type == GeneEffectType.HUNGER_DRIVE:
                strength_delta += 1

            elif gene.effect_type == GeneEffectType.LOW_ACTIVITY:
                strength_delta -= 1
                defense_delta += 1

            elif gene.effect_type == GeneEffectType.HEAT_RESISTANCE:
                temp_pref_delta += 3.0

            elif gene.effect_type == GeneEffectType.COLD_RESISTANCE:
                temp_pref_delta -= 3.0

            elif gene.effect_type == GeneEffectType.RISK_MOVE:
                strength_delta += 1

        return GenomeEffects(
            strength_delta=strength_delta,
            defense_delta=defense_delta,
            temp_pref_delta=temp_pref_delta,
        )
