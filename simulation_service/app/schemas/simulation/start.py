from typing import Optional

from pydantic import BaseModel


class StartSimulationRequest(BaseModel):
    interval_seconds: Optional[float] = None
    max_steps: Optional[int] = None
