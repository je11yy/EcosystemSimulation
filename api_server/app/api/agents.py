from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import AgentCreate, AgentResponse, Response
from app.services.agent.service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def get_agents(
    simulation_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> list[dict]:
    return await AgentService(db).list_by_simulation(simulation_id, current_user.id)


@router.post("", response_model=Response)
async def create_agent(
    agent: AgentCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await AgentService(db).create(agent, current_user.id)
    return Response(success=True, message="Agent created")


@router.delete("/{agent_id}", response_model=Response)
async def delete_agent(agent_id: int, current_user: CurrentUser, db: DbSession) -> Response:
    await AgentService(db).delete(agent_id, current_user.id)
    return Response(success=True, message="Agent deleted")


@router.put("/{agent_id}", response_model=Response)
async def update_agent(
    agent_id: int,
    payload: AgentCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await AgentService(db).update(agent_id, payload, current_user.id)
    return Response(success=True, message="Agent updated")
