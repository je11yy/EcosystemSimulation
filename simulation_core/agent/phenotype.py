from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..config import SimConfig
from ..genome.effect_type import GeneEffectType
from ..genome.models import Genome
from .traits import TraitAggregator

if TYPE_CHECKING:
    from .state import AgentState


@dataclass(frozen=True)
class AgentPhenotype:
    max_hp: float
    strength: float
    defense: float


def build_agent_phenotype(
    state: AgentState,
    genome: Genome,
    cfg: SimConfig,
    traits: TraitAggregator | None = None,
) -> AgentPhenotype:
    traits = traits or TraitAggregator(genome)

    return AgentPhenotype(
        max_hp=max(cfg.hp_min + 1, cfg.hp_max * traits.multiplier(GeneEffectType.MAX_HP)),
        strength=max(
            cfg.strength_min,
            state.base_strength * traits.multiplier(GeneEffectType.STRENGTH),
        ),
        defense=max(
            cfg.defense_min,
            state.base_defense * traits.multiplier(GeneEffectType.DEFENSE),
        ),
    )
