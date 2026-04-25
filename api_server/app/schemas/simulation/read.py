from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.enums import SimulationStatus

from ..base import Node
from .log import SimulationLogRead


class SimulationBase(BaseModel):
    name: str


class SimulationRead(SimulationBase):
    id: int
    user_id: int
    updated_at: datetime
    status: SimulationStatus
    tick: int

    class Config:
        from_attributes = True


class TerritoryResponse(Node):
    food: float
    temperature: float
    food_regen_per_tick: float
    food_capacity: float


class TerritoryEdgeResponse(BaseModel):
    id: int
    source: int
    target: int
    weight: float


class SimulationDetails(SimulationRead):
    territories: list[TerritoryResponse]
    territories_edges: list[TerritoryEdgeResponse]
    last_log: Optional[SimulationLogRead] = None
    logs: list[SimulationLogRead] = Field(default_factory=list)
    logs_count: int = 0
    last_step: Optional[dict] = None


class SimulationBatchRunRequest(BaseModel):
    steps: int = Field(ge=1, le=150)


class SimulationLogListItem(BaseModel):
    id: int
    simulation_id: int
    tick: int
    created_at: datetime

    class Config:
        from_attributes = True
