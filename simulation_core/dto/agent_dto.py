from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional, Sequence


@dataclass(frozen=True)
class AgentGeneDTO:
    id: str
    name: str
    chromosome_id: str
    position: float
    default_active: bool
    threshold: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentGeneEdgeDTO:
    source_gene_id: str
    target_gene_id: str
    weight: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentGeneStateDTO:
    gene_id: str
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

    pregnant: bool
    ticks_to_birth: int
    father_id: Optional[str]

    base_temp_pref: float
    effective_temp_pref: float

    satisfaction: float
    alive: bool

    active_genes: Sequence[str]

    genes: Sequence[AgentGeneDTO]
    gene_edges: Sequence[AgentGeneEdgeDTO]
    gene_states: Sequence[AgentGeneStateDTO]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
