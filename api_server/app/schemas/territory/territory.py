from typing import Optional

from pydantic import BaseModel

from ..base import Position


class TerritoryCreate(BaseModel):
    food: Optional[float] = None
    food_capacity: float
    food_regen_per_tick: float
    temperature: float
    position: Position
    simulation_id: Optional[int] = None


class TerritoryRead(TerritoryCreate):
    id: int
    food: float

    class Config:
        from_attributes = True


class TerritoryEdgeCreate(BaseModel):
    source: int
    target: int
    weight: float
    simulation_id: Optional[int] = None


class TerritoryEdgeRead(TerritoryEdgeCreate):
    id: int

    class Config:
        from_attributes = True
