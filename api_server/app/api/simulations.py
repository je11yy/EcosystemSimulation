from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.schemas import Response, SimulationCreate, SimulationDetails, SimulationRead
from app.services.scenario import ScenarioService
from app.services.simulation.service import SimulationService

router = APIRouter(prefix="/simulations", tags=["simulations"])


class SimulationNameUpdate(BaseModel):
    name: str


class ScenarioPresetRead(BaseModel):
    key: str
    name: str
    description: str


class ScenarioCreateResponse(Response):
    simulation_id: int


@router.get("", response_model=list[SimulationRead])
async def get_simulations(current_user: CurrentUser, db: DbSession) -> list[dict]:
    return await SimulationService(db).list_by_user(current_user.id)


@router.post("", response_model=Response)
async def create_simulation(
    simulation: SimulationCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).create(current_user.id, simulation)
    return Response(success=True, message="Simulation created")


@router.get("/scenarios", response_model=list[ScenarioPresetRead])
async def get_scenario_presets(current_user: CurrentUser, db: DbSession) -> list[dict]:
    return await ScenarioService(db).list_scenarios()


@router.post("/scenarios/{scenario_key}", response_model=ScenarioCreateResponse)
async def create_simulation_from_scenario(
    scenario_key: str,
    current_user: CurrentUser,
    db: DbSession,
) -> ScenarioCreateResponse:
    simulation_id = await ScenarioService(db).create_from_scenario(current_user.id, scenario_key)
    return ScenarioCreateResponse(
        success=True,
        message="Scenario created",
        simulation_id=simulation_id,
    )


@router.get("/{simulation_id}", response_model=SimulationDetails)
async def get_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> dict:
    return await SimulationService(db).get_details(current_user.id, simulation_id)


@router.delete("/{simulation_id}", response_model=Response)
async def delete_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).delete(current_user.id, simulation_id)
    return Response(success=True, message="Simulation deleted")


@router.put("/{simulation_id}/name", response_model=Response)
async def update_simulation_name(
    simulation_id: int,
    payload: SimulationNameUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).rename(current_user.id, simulation_id, payload.name)
    return Response(success=True, message="Simulation renamed")


@router.post("/{simulation_id}/start", response_model=Response)
async def start_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).start(current_user.id, simulation_id)
    return Response(success=True, message="Simulation started")


@router.post("/{simulation_id}/build", response_model=Response)
async def build_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).build_runtime(current_user.id, simulation_id)
    return Response(success=True, message="Simulation built")


@router.post("/{simulation_id}/run", response_model=Response)
async def run_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).start(current_user.id, simulation_id)
    return Response(success=True, message="Simulation running")


@router.post("/{simulation_id}/pause", response_model=Response)
async def pause_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).pause(current_user.id, simulation_id)
    return Response(success=True, message="Simulation paused")


@router.post("/{simulation_id}/stop", response_model=Response)
async def stop_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).stop(current_user.id, simulation_id)
    return Response(success=True, message="Simulation stopped")


@router.post("/{simulation_id}/step", response_model=Response)
async def step_simulation(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await SimulationService(db).step(current_user.id, simulation_id)
    return Response(success=True, message="Simulation stepped")
