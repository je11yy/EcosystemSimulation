from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional, Sequence

from simulation_core.agents.genome.effect_type import GeneEffectType


@dataclass(frozen=True)
class AgentGeneDTO:
    id: int
    name: str
    chromosome_id: str
    position: float
    default_active: bool
    threshold: float
    effect_type: GeneEffectType

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentGeneEdgeDTO:
    source_gene_id: int
    target_gene_id: int
    weight: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentGeneStateDTO:
    gene_id: int
    is_active: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentDTO:
    id: str
    location: str

    hunger: int
    hp: int

    base_strength: int
    effective_strength: int

    base_defense: int
    effective_defense: int

    sex: Literal["male", "female"]

    species_group: str

    pregnant: bool
    ticks_to_birth: int
    father_id: Optional[str]

    base_temp_pref: float
    effective_temp_pref: float

    hunt_cooldown: int

    satisfaction: float
    alive: bool

    active_genes: Sequence[int]

    genes: Sequence[AgentGeneDTO]
    gene_edges: Sequence[AgentGeneEdgeDTO]
    gene_states: Sequence[AgentGeneStateDTO]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
