from fastapi import APIRouter

from app.schemas.simulation import (
    BuildSimulationRequest,
    RuntimeDrainResponse,
    RuntimeStatusResponse,
    RuntimeStepResponse,
    StartSimulationRequest,
    StopSimulationResponse,
)
from app.services.runtime_manager import runtime_manager

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.post("/build", response_model=RuntimeStatusResponse)
async def build_simulation(payload: BuildSimulationRequest) -> RuntimeStatusResponse:
    return await runtime_manager.build(payload)


@router.post("/{simulation_id}/step", response_model=RuntimeStepResponse)
async def step_simulation(simulation_id: int) -> RuntimeStepResponse:
    return await runtime_manager.step(simulation_id)


@router.post("/{simulation_id}/start", response_model=RuntimeStatusResponse)
async def start_simulation(
    simulation_id: int,
    payload: StartSimulationRequest,
) -> RuntimeStatusResponse:
    return await runtime_manager.start(simulation_id, payload)


@router.post("/{simulation_id}/pause", response_model=RuntimeStatusResponse)
async def pause_simulation(simulation_id: int) -> RuntimeStatusResponse:
    return await runtime_manager.pause(simulation_id)


@router.post("/{simulation_id}/drain", response_model=RuntimeDrainResponse)
async def drain_simulation_results(simulation_id: int) -> dict:
    return await runtime_manager.drain(simulation_id)


@router.post("/{simulation_id}/stop", response_model=StopSimulationResponse)
async def stop_simulation(simulation_id: int) -> StopSimulationResponse:
    stopped = await runtime_manager.stop(simulation_id)
    return StopSimulationResponse(simulation_id=simulation_id, stopped=stopped)


@router.get("/{simulation_id}/state", response_model=RuntimeStatusResponse)
async def get_simulation_state(simulation_id: int) -> RuntimeStatusResponse:
    return runtime_manager.status(simulation_id, include_snapshot=True)
