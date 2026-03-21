import asyncio
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal, get_db
from app.schemas.simulation import SimulationCreate, SimulationRead
from app.services.engine_persister import EnginePersister
from app.services.simulation_client import SimulationClient
from app.services.simulation_runtime_manager import SimulationRuntimeManager
from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post("", response_model=SimulationRead)
async def create_simulation(
    payload: SimulationCreate,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    simulation = await service.create_simulation(user_id=user_id, name=payload.name)
    return simulation


@router.get("/{simulation_id}", response_model=SimulationRead)
async def get_simulation(
    simulation_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    simulation = await service.get_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return simulation


@router.get("", response_model=list[SimulationRead])
async def list_simulations(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    return await service.list_user_simulations(user_id=user_id)


@router.post("/{simulation_id}/start")
async def start_simulation(
    simulation_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    simulation = await service.get_full_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    payload = service.mapper.to_init_dto(simulation)

    client = SimulationClient()
    runtime_response = await client.init_runtime(payload)

    simulation.status = "loaded"
    await db.commit()
    await db.refresh(simulation)

    return {
        "simulation_id": simulation_id,
        "runtime": runtime_response,
        "status": simulation.status,
    }


@router.post("/{simulation_id}/step")
async def step_simulation(
    simulation_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    simulation = await service.get_full_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    client = SimulationClient()
    runtime_response = await client.step_runtime(simulation_id)

    persister = EnginePersister(db)
    await persister.persist_state(simulation, runtime_response["state"])

    return {
        "simulation_id": simulation_id,
        "state": runtime_response["state"],
        "step_result": runtime_response["step_result"],
    }


@router.get("/{simulation_id}/state")
async def get_simulation_state(
    simulation_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    simulation = await service.get_full_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    payload = service.mapper.to_init_dto(simulation)

    return {
        "simulation_id": simulation_id,
        "tick": payload.tick,
        "territories": [territory.model_dump() for territory in payload.territories],
        "territory_edges": [edge.model_dump() for edge in payload.territory_edges],
        "agents": [agent.model_dump() for agent in payload.agents],
    }


@router.post("/{simulation_id}/stop")
async def stop_simulation(
    simulation_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    simulation = await service.get_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    runtime_manager = request.app.state.simulation_runtime_manager
    client = SimulationClient()

    await runtime_manager.stop_loop(simulation_id)
    runtime_response = await client.stop_runtime(simulation_id)

    await service.set_status(simulation, "stopped")

    return {
        "simulation_id": simulation_id,
        "runtime": runtime_response,
        "status": simulation.status,
    }


async def _run_simulation_loop(
    simulation_id: int, runtime_manager: SimulationRuntimeManager
) -> None:
    client = SimulationClient()

    try:
        while True:
            async with SessionLocal() as db:
                service = SimulationService(db)
                simulation = await service.get_full_simulation(simulation_id)

                if simulation is None:
                    break

                if simulation.status != "running":
                    break

                runtime_response = await client.step_runtime(simulation_id)

                persister = EnginePersister(db)
                await persister.persist_state(simulation, runtime_response["state"])

            await asyncio.sleep(settings.simulation_step_interval_seconds)

    except asyncio.CancelledError:
        raise
    finally:
        await runtime_manager.cleanup_finished(simulation_id)


@router.post("/{simulation_id}/run")
async def run_simulation(
    simulation_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    simulation = await service.get_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    runtime_manager = request.app.state.simulation_runtime_manager
    client = SimulationClient()

    # runtime должен быть загружен
    if simulation.status == "draft" or simulation.status == "stopped":
        full_simulation = await service.get_full_simulation(simulation_id)
        if full_simulation is None:
            raise HTTPException(status_code=404, detail="Simulation not found")

        payload = service.mapper.to_init_dto(full_simulation)
        await client.init_runtime(payload)
        simulation = full_simulation

    if runtime_manager.is_running(simulation_id):
        return {
            "simulation_id": simulation_id,
            "status": simulation.status,
            "message": "Simulation is already running",
        }

    await service.set_status(simulation, "running")

    started = await runtime_manager.start_loop(
        simulation_id=simulation_id,
        coro_factory=lambda: _run_simulation_loop(simulation_id, runtime_manager),
    )

    return {
        "simulation_id": simulation_id,
        "status": "running",
        "started": started,
    }


@router.post("/{simulation_id}/pause")
async def pause_simulation(
    simulation_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    simulation = await service.get_simulation(simulation_id)

    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    runtime_manager = request.app.state.simulation_runtime_manager

    await service.set_status(simulation, "paused")
    stopped = await runtime_manager.stop_loop(simulation_id)

    return {
        "simulation_id": simulation_id,
        "status": "paused",
        "loop_stopped": stopped,
    }
