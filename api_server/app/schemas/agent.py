from typing import Optional

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    territory_id: int
    genome_template_id: int

    hunger: int = Field(ge=0, le=5, default=0)
    hp: int = Field(ge=0, le=5, default=5)

    base_strength: int = Field(ge=1, le=5)
    base_defense: int = Field(ge=1, le=5)

    sex: str
    pregnant: bool = False
    ticks_to_birth: int = 0
    father_id: Optional[int] = None

    base_temp_pref: float = 20.0
    satisfaction: float = 1.0
    alive: bool = True


class AgentRead(BaseModel):
    id: int
    simulation_id: int
    territory_id: int

    hunger: int
    hp: int

    base_strength: int
    base_defense: int

    sex: str
    pregnant: bool
    ticks_to_birth: int
    father_id: Optional[int] = None

    base_temp_pref: float
    satisfaction: float
    alive: bool

    model_config = {"from_attributes": True}
