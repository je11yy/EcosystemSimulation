from fastapi import APIRouter

from app.schemas.simulation import RunBatchSimulationRequest, RunBatchSimulationResponse
from app.services.runtime_manager import runtime_manager

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.post("/run-batch", response_model=RunBatchSimulationResponse)
async def run_batch_simulation(payload: RunBatchSimulationRequest) -> RunBatchSimulationResponse:
    return await runtime_manager.run_batch(payload)
