from dataclasses import dataclass

from simulation_core.types import TerritoryId


@dataclass
class TerritoryState:
    id: TerritoryId
    food: float
    temperature: float

    # добавить реген еды?
    # food_regen_per_tick: float = 0.5
