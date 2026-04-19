from typing import Optional

from pydantic import BaseModel


class RuntimeAgent(BaseModel):
    id: int
    sex: str
    territory_id: int
    genome_id: Optional[int] = None

    hunger: float = 0.0
    hp: float = 5.0
    strength: float = 1.0
    defense: float = 1.0
    temp_pref: float = 20.0
    satisfaction: float = 3.0
    pregnant: bool = False
    ticks_to_birth: int = 0
    hunt_cooldown: int = 0
    is_alive: bool = True
