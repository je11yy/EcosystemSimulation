from typing import Any

from pydantic import BaseModel, Field

from .init import BuildSimulationRequest
from .state import RuntimeSnapshot


class RunBatchSimulationRequest(BaseModel):
    build: BuildSimulationRequest
    steps: int = Field(ge=1, le=150)


class RuntimeTickResult(BaseModel):
    result: dict[str, Any] = Field(default_factory=dict)
    snapshot: RuntimeSnapshot


class RunBatchSimulationResponse(BaseModel):
    simulation_id: int
    steps: int
    tick_results: list[RuntimeTickResult] = Field(default_factory=list)
    final_snapshot: RuntimeSnapshot
