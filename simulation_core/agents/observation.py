from dataclasses import dataclass
from typing import Literal, Sequence

from simulation_core.types import IndividualId, TerritoryId


@dataclass(frozen=True)
class ObservedIndividual:
    id: IndividualId
    sex: Literal["male", "female"]
    species_group: str
    hunger: int
    alive: bool
    effective_strength: int
    effective_defense: int
    effective_temp_pref: float


@dataclass(frozen=True)
class ObservedTerritory:
    id: TerritoryId
    food: float
    food_capacity: float
    temperature: float
    movement_cost: float
    occupant_count: int


@dataclass(frozen=True)
class Observation:
    current_id: TerritoryId
    individuals_here: Sequence[ObservedIndividual]
    neighbor_territories: Sequence[ObservedTerritory]

    def get_individual(self, individual_id: IndividualId) -> ObservedIndividual | None:
        for individual in self.individuals_here:
            if individual.id == individual_id:
                return individual
        return None

    def get_neighbor_territory(self, territory_id: TerritoryId) -> ObservedTerritory | None:
        for territory in self.neighbor_territories:
            if territory.id == territory_id:
                return territory
        return None
