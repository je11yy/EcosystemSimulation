from dataclasses import dataclass

from ..enums import AgentSex


@dataclass(frozen=True)
class ObservedAgent:
    id: int
    sex: AgentSex
    hp: float
    strength: float
    defense: float
    is_alive: bool = True


@dataclass(frozen=True)
class ObservedTerritory:
    id: int
    temperature: float
    food: float
    movement_cost: float
    occupant_count: int


@dataclass
class Observation:
    current_territory: ObservedTerritory
    agents: list[ObservedAgent]
    neighboring_territories: list[ObservedTerritory]
