from dataclasses import dataclass
from typing import Sequence

from simulation_core.types import IndividualId, TerritoryId


# наблюдение для агента --- то, что он видит и на основе чего принимает решение
@dataclass(frozen=True)
class Observation:
    """Наблюдение агента об окружающем мире.

    Содержит информацию, доступную агенту для принятия решений:
    текущую территорию, других агентов на ней и соседние территории.
    """

    current_id: TerritoryId  # ID текущей территории, где находится агент
    individuals_here: Sequence[IndividualId]  # ID других агентов на этой территории
    neighbor_territories: Sequence[TerritoryId]  # ID соседних территорий, куда можно переместиться
