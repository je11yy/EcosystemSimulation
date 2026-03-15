from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional, Sequence

from simulation_core.types import IndividualId, TerritoryId


@dataclass(frozen=True)
class AgentDTO:
    """DTO (Data Transfer Object) для передачи данных об агенте."""

    id: IndividualId  # Уникальный ID агента
    location: TerritoryId  # ID территории расположения

    hunger: int  # Уровень голода
    hp: int

    base_strength: int  # Уровень силы
    effective_strength: int

    base_defense: int  # Уровень защиты
    effective_defense: int

    sex: Literal["male", "female"]  # Пол агента

    pregnant: bool  # Беременна ли самка
    ticks_to_birth: int  # Тиков до рождения потомства
    father_id: Optional[IndividualId]  # ID отца

    base_temp_pref: float  # Предпочитаемая температура
    effective_temp_pref: float  # Эффективная предпочтительная температура
    satisfaction: float  # Уровень удовлетворенности

    alive: bool  # Жив ли агент

    active_genes: Sequence[str]  # Список ID активных генов

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
