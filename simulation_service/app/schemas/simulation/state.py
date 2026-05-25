from typing import Any, Optional

from pydantic import BaseModel, Field


class RuntimeSnapshot(BaseModel):
    simulation_id: int
    tick: int
    status: str
    agents: list[dict[str, Any]] = Field(default_factory=list)
    territories: list[dict[str, Any]] = Field(default_factory=list)
    last_result: Optional[dict[str, Any]] = None
