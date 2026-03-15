from dataclasses import dataclass
from enum import Enum
from typing import Optional

from simulation_core.types import IndividualId, TerritoryId


class ActionType(str, Enum):
    """Типы действий, доступных агентам в симуляции."""

    EAT = "eat"  # Есть еду на текущей территории
    MOVE = "move"  # Переместиться на другую территорию
    MATE = "mate"  # Спариться с партнером
    REST = "rest"  # Отдохнуть (ничего не делать)


@dataclass(frozen=True)
class ActionOption:
    """Вариант действия агента.

    Определяет конкретное действие с необходимыми параметрами.

    EAT  -> без параметров (ест на текущей территории)
    MOVE -> нужен to_territory (ID территории назначения)
    MATE -> нужен partner_id (ID партнера для спаривания)
    REST -> без параметров (просто отдых)
    """

    type: ActionType  # Тип действия
    to_territory: Optional[TerritoryId] = None  # Для MOVE: куда перемещаться
    partner_id: Optional[IndividualId] = None  # Для MATE: с кем спариваться
    tag: Optional[str] = None  # Дополнительный тег для идентификации
