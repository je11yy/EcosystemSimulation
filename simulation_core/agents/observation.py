from dataclasses import dataclass
from typing import Sequence

from simulation_core.types import IndividualId, TerritoryId


# наблюдение для агента --- то, что он видит и на основе чего принимает решение
@dataclass(frozen=True)
class Observation:
    current_id: TerritoryId  # id текущей территории
    individuals_here: Sequence[IndividualId]  # id соседей (на текущей территории)
    neighbor_territories: Sequence[TerritoryId]  # соседние территории
