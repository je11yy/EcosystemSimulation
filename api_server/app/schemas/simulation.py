from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SimulationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class SimulationRead(BaseModel):
    id: int
    user_id: int
    name: str
    status: str
    tick: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SimulationPresetCreate(BaseModel):
    preset: Literal[
        "base_demo",
        "food_scarcity",
        "cold_climate",
        "predator_dominance",
        "high_density",
        "social_tolerance",
    ]
    name: str | None = None
