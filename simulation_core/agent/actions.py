from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    EAT = "eat"
    MOVE = "move"
    MATE = "mate"
    REST = "rest"
    HUNT = "hunt"


@dataclass(frozen=True)
class ActionOption:
    type: ActionType
    to_territory: Optional[int] = None
    partner_id: Optional[int] = None
    target_id: Optional[int] = None
