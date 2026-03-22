from typing import Optional

from pydantic import BaseModel, Field


class TerritoryCreate(BaseModel):
    food: float = Field(ge=0)
    temperature: float
    food_regen_per_tick: float = Field(ge=0, default=0.0)
    food_capacity: float = Field(gt=0, default=10.0)
    x: Optional[int] = None
    y: Optional[int] = None


class TerritoryUpdate(BaseModel):
    food: Optional[float] = Field(default=None, ge=0)
    temperature: Optional[float] = None
    food_regen_per_tick: Optional[float] = Field(default=None, ge=0)
    food_capacity: Optional[float] = Field(default=None, gt=0)
    x: Optional[int] = None
    y: Optional[int] = None


class TerritoryRead(BaseModel):
    id: int
    simulation_id: int
    food: float
    temperature: float
    food_regen_per_tick: float
    food_capacity: float
    x: Optional[int] = None
    y: Optional[int] = None

    model_config = {"from_attributes": True}
