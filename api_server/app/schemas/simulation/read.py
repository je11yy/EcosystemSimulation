from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.enums import SimulationStatus

from ..base import Node
from .log import SimulationLogRead


class SimulationBase(BaseModel):
    """Base simulation model."""

    name: str


class SimulationRead(SimulationBase):
    """Simulation list/read response."""

    id: int
    user_id: int
    updated_at: datetime
    status: SimulationStatus
    tick: int

    class Config:
        from_attributes = True


class TerritoryResponse(Node):
    """Territory with all data."""

    food: float
    temperature: float
    food_regen_per_tick: float
    food_capacity: float


class TerritoryEdgeResponse(BaseModel):
    """Territory edge response."""

    id: int
    source: int
    target: int
    weight: float


class SimulationDetails(SimulationRead):
    """Simulation with all details."""

    territories: list[TerritoryResponse]
    territories_edges: list[TerritoryEdgeResponse]
    last_log: Optional[SimulationLogRead] = None
    last_step: Optional[dict] = None


class SimulationLogListItem(BaseModel):
    """Compact simulation log item for history lists."""

    id: int
    simulation_id: int
    tick: int
    created_at: datetime

    class Config:
        from_attributes = True
