import asyncio
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal, get_db
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentRead
from app.schemas.simulation import SimulationCreate, SimulationRead
from app.schemas.territory import TerritoryCreate, TerritoryRead, TerritoryUpdate
from app.schemas.territory_edge import TerritoryEdgeCreate, TerritoryEdgeRead
from app.services.builtin_genome_template_seeder import BuiltinGenomeTemplateSeeder
from app.services.demo_simulation_seeder import DemoSimulationSeeder
from app.services.engine_persister import EnginePersister
from app.services.simulation_client import SimulationClient
from app.services.simulation_runtime_manager import SimulationRuntimeManager
from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulations", tags=["simulations"])


async def _ensure_user_exists(db: AsyncSession, user_id: int) -> None:
    existing = await db.execute(select(User).where(User.id == user_id))
    if existing.scalar_one_or_none() is None:
        db.add(
            User(
                id=user_id,
                email=f"user{user_id}@example.com",
                hashed_password="placeholder",
            )
        )
        await db.flush()


@router.post("", response_model=SimulationRead)
async def create_simulation(
    payload: SimulationCreate,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _ensure_user_exists(db, user_id)
    await BuiltinGenomeTemplateSeeder().seed_for_user(db, user_id)

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
    await _ensure_user_exists(db, user_id)
    await BuiltinGenomeTemplateSeeder().seed_for_user(db, user_id)
    await DemoSimulationSeeder().seed_for_user(db, user_id)

    service = SimulationService(db)
    return await service.list_user_simulations(user_id)


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
        "territory_edges": [
            {
                "id": edge.id,
                "source_id": str(edge.source_territory_id),
                "target_id": str(edge.target_territory_id),
                "movement_cost": edge.movement_cost,
            }
            for edge in simulation.territory_edges
        ],
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


@router.post("/{simulation_id}/territories", response_model=TerritoryRead)
async def create_territory(
    simulation_id: int,
    payload: TerritoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    territory = await service.create_territory(simulation_id, payload)

    if territory is None:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return territory


@router.post("/{simulation_id}/agents", response_model=AgentRead)
async def create_agent(
    simulation_id: int,
    payload: AgentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    agent, error = await service.create_agent(simulation_id, payload)

    if error == "simulation_not_found":
        raise HTTPException(status_code=404, detail="Simulation not found")

    if error == "territory_not_found":
        raise HTTPException(status_code=404, detail="Territory not found in simulation")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return agent


@router.post("/{simulation_id}/edges", response_model=TerritoryEdgeRead)
async def create_territory_edge(
    simulation_id: int,
    payload: TerritoryEdgeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    edge, error = await service.create_territory_edge(simulation_id, payload)

    if error == "simulation_not_found":
        raise HTTPException(status_code=404, detail="Simulation not found")

    if error == "source_not_found":
        raise HTTPException(status_code=404, detail="Source territory not found in simulation")

    if error == "target_not_found":
        raise HTTPException(status_code=404, detail="Target territory not found in simulation")

    if error == "same_territory":
        raise HTTPException(status_code=400, detail="Cannot connect territory to itself")

    if error == "edge_already_exists":
        raise HTTPException(status_code=400, detail="Edge already exists")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return edge


@router.patch("/{simulation_id}/territories/{territory_id}", response_model=TerritoryRead)
async def update_territory(
    simulation_id: int,
    territory_id: int,
    payload: TerritoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = SimulationService(db)
    territory, error = await service.update_territory(simulation_id, territory_id, payload)

    if error == "simulation_not_found":
        raise HTTPException(status_code=404, detail="Simulation not found")

    if error == "territory_not_found":
        raise HTTPException(status_code=404, detail="Territory not found")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return territory


@router.delete("/{simulation_id}/territories/{territory_id}")
async def delete_territory(
    simulation_id: int,
    territory_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    error = await service.delete_territory(simulation_id, territory_id)

    if error == "simulation_not_found":
        raise HTTPException(status_code=404, detail="Simulation not found")

    if error == "territory_not_found":
        raise HTTPException(status_code=404, detail="Territory not found")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return {"ok": True, "territory_id": territory_id}


@router.delete("/{simulation_id}/edges/{edge_id}")
async def delete_territory_edge(
    simulation_id: int,
    edge_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    error = await service.delete_territory_edge(simulation_id, edge_id)

    if error == "simulation_not_found":
        raise HTTPException(status_code=404, detail="Simulation not found")

    if error == "edge_not_found":
        raise HTTPException(status_code=404, detail="Edge not found")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return {"ok": True, "edge_id": edge_id}


@router.delete("/{simulation_id}/agents/{agent_id}")
async def delete_agent(
    simulation_id: int,
    agent_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = SimulationService(db)
    error = await service.delete_agent(simulation_id, agent_id)

    if error == "simulation_not_found":
        raise HTTPException(status_code=404, detail="Simulation not found")

    if error == "agent_not_found":
        raise HTTPException(status_code=404, detail="Agent not found")

    simulation = await service.get_full_simulation(simulation_id)
    client = SimulationClient()

    try:
        await client.stop_runtime(simulation_id)
    except Exception:
        pass

    if simulation is not None and simulation.status in {"loaded", "running", "paused"}:
        init_payload = service.mapper.to_init_dto(simulation)
        await client.init_runtime(init_payload)

    return {"ok": True, "agent_id": agent_id}
