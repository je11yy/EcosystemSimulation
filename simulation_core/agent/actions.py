from dataclasses import dataclass
from typing import Optional

from simulation_core.enums import AgentActionType


@dataclass(frozen=True)
class ActionOption:
    type: AgentActionType
    to_territory: Optional[int] = None
    partner_id: Optional[int] = None
    target_id: Optional[int] = None


@dataclass(frozen=True)
class ScoredOption:
    option: ActionOption
    utility: float
