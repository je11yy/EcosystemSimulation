from typing import Any

from app.mappers.common import position
from app.models import Territory, TerritoryEdge


def territory_to_dict(territory: Territory) -> dict[str, Any]:
    return {
        "id": territory.id,
        "food_capacity": territory.food_capacity,
        "food_regen_per_tick": territory.food_regen_per_tick,
        "temperature": territory.temperature,
        "position": position(territory.x, territory.y),
        "simulation_id": territory.simulation_id,
        "food": territory.food,
    }


def territory_edge_to_dict(edge: TerritoryEdge) -> dict[str, Any]:
    return {
        "id": edge.id,
        "source": edge.source_id,
        "target": edge.target_id,
        "weight": edge.weight,
    }
