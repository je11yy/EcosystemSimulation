from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DbSession
from app.schemas import (
    Position,
    Response,
    TerritoryCreate,
    TerritoryEdgeCreate,
    TerritoryEdgeRead,
    TerritoryRead,
)
from app.services.territory.service import TerritoryService

router = APIRouter(prefix="/territories", tags=["territories"])


class EdgeWeightUpdate(BaseModel):
    weight: float


@router.get("", response_model=list[TerritoryRead])
async def get_territories(simulation_id: int, db: DbSession) -> list[dict]:
    return await TerritoryService(db).list_by_simulation(simulation_id)


@router.post("", response_model=Response)
async def create_territory(
    territory: TerritoryCreate,
    db: DbSession,
) -> Response:
    await TerritoryService(db).create(territory)
    return Response(success=True, message="Territory created")


@router.get("/edges", response_model=list[TerritoryEdgeRead])
async def get_edges(simulation_id: int, db: DbSession) -> list[dict]:
    return await TerritoryService(db).list_edges_by_simulation(simulation_id)


@router.post("/edges", response_model=Response)
async def create_edge(edge: TerritoryEdgeCreate, db: DbSession) -> Response:
    await TerritoryService(db).create_edge(edge)
    return Response(success=True, message="Territory edge created")


@router.delete("/edges/{edge_id}", response_model=Response)
async def delete_edge(edge_id: int, db: DbSession) -> Response:
    await TerritoryService(db).delete_edge(edge_id)
    return Response(success=True, message="Territory edge deleted")


@router.put("/edges/{edge_id}", response_model=Response)
async def update_edge_weight(
    edge_id: int,
    payload: EdgeWeightUpdate,
    db: DbSession,
) -> Response:
    await TerritoryService(db).update_edge_weight(edge_id, payload.weight)
    return Response(success=True, message="Territory edge updated")


@router.delete("/{territory_id}", response_model=Response)
async def delete_territory(territory_id: int, db: DbSession) -> Response:
    await TerritoryService(db).delete(territory_id)
    return Response(success=True, message="Territory deleted")


@router.put("/{territory_id}", response_model=Response)
async def update_territory(
    territory_id: int,
    payload: TerritoryCreate,
    db: DbSession,
) -> Response:
    await TerritoryService(db).update(territory_id, payload)
    return Response(success=True, message="Territory updated")


@router.put("/{territory_id}/position", response_model=Response)
async def update_territory_position(
    territory_id: int,
    position: Position,
    db: DbSession,
) -> Response:
    await TerritoryService(db).update_position(territory_id, position)
    return Response(success=True, message="Territory position updated")
