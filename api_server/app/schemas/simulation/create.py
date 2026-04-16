from pydantic import BaseModel


class SimulationCreate(BaseModel):
    """Simulation create request."""

    name: str
