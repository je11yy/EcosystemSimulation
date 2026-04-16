from typing import Optional

from pydantic import BaseModel

from app.enums import AgentSex

from .create import AgentCreate


class AgentRead(AgentCreate):
    """Agent read response"""

    id: int
    hunger: float
    hp: float
    strength: float
    defense: float
    temp_pref: float
    pregnant: bool
    ticks_to_birth: Optional[int] = None
    satisfaction: float

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    """Agent response with full data"""

    id: int
    sex: AgentSex
    territory_id: int
    genome_id: Optional[int] = None
    hunger: float
    hp: float
    strength: float
    defense: float
    temp_pref: float
    satisfaction: float
    pregnant: bool
    ticks_to_birth: Optional[int] = None

    class Config:
        from_attributes = True
