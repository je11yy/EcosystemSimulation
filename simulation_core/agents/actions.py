from dataclasses import dataclass
from enum import Enum
from typing import Optional

from simulation_core.types import IndividualId, TerritoryId


class ActionType(str, Enum):
    EAT = "eat"
    MOVE = "move"
    MATE = "mate"
    REST = "rest"
    HUNT = "hunt"


@dataclass(frozen=True)
class ActionOption:
    type: ActionType
    to_territory: Optional[TerritoryId] = None
    partner_id: Optional[IndividualId] = None
    target_id: Optional[IndividualId] = None
    tag: Optional[str] = None
