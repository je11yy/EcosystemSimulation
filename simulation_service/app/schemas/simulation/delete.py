from pydantic import BaseModel


class StopSimulationResponse(BaseModel):
    simulation_id: int
    stopped: bool
