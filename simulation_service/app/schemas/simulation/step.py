from typing import Any

from pydantic import BaseModel, Field

from .state import RuntimeSnapshot


class RuntimeStepResponse(BaseModel):
    simulation_id: int
    tick: int
    result: dict[str, Any] = Field(default_factory=dict)
    snapshot: RuntimeSnapshot
