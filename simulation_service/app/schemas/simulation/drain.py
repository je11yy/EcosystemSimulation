from typing import Any

from pydantic import BaseModel, Field

from .state import RuntimeSnapshot


class RuntimeDrainResponse(BaseModel):
    simulation_id: int
    results: list[dict[str, Any]] = Field(default_factory=list)
    dropped_results_count: int = 0
    snapshot: RuntimeSnapshot
