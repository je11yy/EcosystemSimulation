from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas import AgentCreate, AgentResponse, Response
from app.services.agent.service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def get_agents(simulation_id: int, db: DbSession) -> list[dict]:
    return await AgentService(db).list_by_simulation(simulation_id)


@router.post("", response_model=Response)
async def create_agent(agent: AgentCreate, db: DbSession) -> Response:
    await AgentService(db).create(agent)
    return Response(success=True, message="Agent created")


@router.delete("/{agent_id}", response_model=Response)
async def delete_agent(agent_id: int, db: DbSession) -> Response:
    await AgentService(db).delete(agent_id)
    return Response(success=True, message="Agent deleted")


@router.put("/{agent_id}", response_model=Response)
async def update_agent(
    agent_id: int,
    payload: AgentCreate,
    db: DbSession,
) -> Response:
    await AgentService(db).update(agent_id, payload)
    return Response(success=True, message="Agent updated")
