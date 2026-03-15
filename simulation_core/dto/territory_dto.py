from dataclasses import asdict, dataclass
from typing import Any

from simulation_core.types import TerritoryId


@dataclass(frozen=True)
class TerritoryDTO:
    """DTO для передачи данных о территории.

    Содержит состояние территории: запасы еды, температуру,
    параметры регенерации и вместимости.
    """

    id: TerritoryId  # Уникальный ID территории
    food: float  # Текущий запас еды
    temperature: float  # Температура территории
    food_regen_per_tick: float  # Количество еды, регенерируемое за тик
    food_capacity: float  # Максимальная вместимость еды

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
