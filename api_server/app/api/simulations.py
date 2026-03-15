from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.simulation import SimulationCreate, SimulationRead
from app.services.simulation_client import SimulationClient
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

    return {
        "simulation_id": simulation_id,
        "runtime": runtime_response,
    }
