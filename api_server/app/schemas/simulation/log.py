from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.enums import AgentActionType


class AgentDecision(BaseModel):
    agent_id: int
    action: AgentActionType
    to_territory: Optional[int] = None
    partner_id: Optional[int] = None
    target_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    eat: int = 0
    move: int = 0
    mate: int = 0
    rest: int = 0
    hunt: int = 0
    deaths: int = 0
    births: int = 0
    fights: int = 0


class TickMetrics(BaseModel):
    alive_population: int = 0
    avg_hunger: float = 0.0
    avg_satisfaction: float = 0.0
    occupancy_by_territory: Dict[int, int] = Field(default_factory=dict)
    deaths_by_reason: Dict[str, int] = Field(default_factory=dict)
    successful_hunts: int = 0
    unsuccessful_hunts: int = 0
    consumed_food: int = 0


class StepEvents(BaseModel):
    applied_results: List[Dict[str, Any]] = Field(default_factory=list)
    deaths: List[Dict[str, Any]] = Field(default_factory=list)
    births: List[Dict[str, Any]] = Field(default_factory=list)
    fights: List[Dict[str, Any]] = Field(default_factory=list)
    hunts: List[Dict[str, Any]] = Field(default_factory=list)


class SimulationLogCreate(BaseModel):
    simulation_id: int
    tick: int
    agent_decisions: List[AgentDecision] = Field(default_factory=list)
    step_result: StepResult = Field(default_factory=StepResult)
    metrics: TickMetrics = Field(default_factory=TickMetrics)
    events: StepEvents = Field(default_factory=StepEvents)


class SimulationLogRead(SimulationLogCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
