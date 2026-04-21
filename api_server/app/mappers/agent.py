from typing import Any

from app.models import Agent


def agent_to_dict(agent: Agent) -> dict[str, Any]:
    return {
        "id": agent.id,
        "sex": agent.sex,
        "territory_id": agent.territory_id,
        "genome_id": agent.genome_id,
        "is_alive": agent.is_alive,
        "hunger": agent.hunger,
        "hp": agent.hp,
        "strength": agent.strength,
        "defense": agent.defense,
        "temp_pref": agent.temp_pref,
        "satisfaction": agent.satisfaction,
        "pregnant": agent.pregnant,
        "ticks_to_birth": agent.ticks_to_birth,
    }
