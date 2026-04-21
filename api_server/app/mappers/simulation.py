from typing import Any

from app.mappers.common import iso
from app.mappers.territory import territory_edge_to_dict, territory_to_dict
from app.models import Simulation, SimulationLog, Territory, TerritoryEdge


def log_to_dict(log: SimulationLog | None) -> dict[str, Any] | None:
    if log is None:
        return None
    return {
        "id": log.id,
        "simulation_id": log.simulation_id,
        "tick": log.tick,
        "agent_decisions": log.agent_decisions,
        "step_result": log.step_result,
        "metrics": log.metrics,
        "events": log.events,
        "created_at": iso(log.created_at),
    }


def simulation_to_dict(simulation: Simulation, user_id: int | None = None) -> dict[str, Any]:
    return {
        "id": simulation.id,
        "name": simulation.name,
        "user_id": user_id if user_id is not None else simulation.user_id,
        "updated_at": iso(simulation.updated_at),
        "status": simulation.status,
        "tick": simulation.tick,
    }


def simulation_details_to_dict(
    simulation: Simulation,
    territories: list[Territory],
    edges: list[TerritoryEdge],
) -> dict[str, Any]:
    last_log = simulation.last_log
    logs = sorted(simulation.logs, key=lambda log: log.tick)
    visible_logs = logs[-20:]
    return {
        **simulation_to_dict(simulation),
        "territories": [territory_to_dict(territory) for territory in territories],
        "territories_edges": [territory_edge_to_dict(edge) for edge in edges],
        "last_log": log_to_dict(last_log),
        "logs": [log_to_dict(log) for log in visible_logs],
        "logs_count": len(logs),
        "last_step": last_log.step_result if last_log else None,
    }
