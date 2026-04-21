from pydantic import BaseModel


class SimulationCreate(BaseModel):
    name: str
