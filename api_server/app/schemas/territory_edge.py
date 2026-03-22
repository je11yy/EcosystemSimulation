from pydantic import BaseModel, Field


class TerritoryEdgeCreate(BaseModel):
    source_territory_id: int
    target_territory_id: int
    movement_cost: float = Field(gt=0, default=1.0)


class TerritoryEdgeRead(BaseModel):
    id: int
    simulation_id: int
    source_territory_id: int
    target_territory_id: int
    movement_cost: float

    model_config = {"from_attributes": True}
