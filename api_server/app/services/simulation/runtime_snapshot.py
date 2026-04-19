from typing import Any

from app.mappers.genome import gene_edge_to_dict, gene_to_dict
from app.mappers.territory import territory_edge_to_dict, territory_to_dict
from app.models import Agent, Genome, Simulation, Territory, TerritoryEdge


def build_runtime_payload(
    simulation: Simulation,
    territories: list[Territory],
    territory_edges: list[TerritoryEdge],
    agents: list[Agent],
    genomes: list[Genome],
) -> dict[str, Any]:
    return {
        "simulation_id": simulation.id,
        "tick": simulation.tick,
        "territories": [_territory_payload(territory) for territory in territories],
        "territory_edges": [_territory_edge_payload(edge) for edge in territory_edges],
        "agents": [_agent_payload(agent) for agent in agents],
        "genomes": [_genome_payload(genome) for genome in genomes],
    }


def _territory_payload(territory: Territory) -> dict[str, Any]:
    data = territory_to_dict(territory)
    return {
        "id": data["id"],
        "food": data["food"],
        "temperature": data["temperature"],
        "food_regen_per_tick": data["food_regen_per_tick"],
        "food_capacity": data["food_capacity"],
    }


def _territory_edge_payload(edge: TerritoryEdge) -> dict[str, Any]:
    data = territory_edge_to_dict(edge)
    return {
        "id": data["id"],
        "source": data["source"],
        "target": data["target"],
        "weight": data["weight"],
    }


def _agent_payload(agent: Agent) -> dict[str, Any]:
    return {
        "id": agent.id,
        "sex": agent.sex,
        "territory_id": agent.territory_id,
        "genome_id": agent.genome_id,
        "hunger": agent.hunger,
        "hp": agent.hp,
        "strength": agent.strength,
        "defense": agent.defense,
        "temp_pref": agent.temp_pref,
        "satisfaction": agent.satisfaction,
        "pregnant": agent.is_pregnant,
        "ticks_to_birth": agent.ticks_to_birth or 0,
        "hunt_cooldown": agent.hunt_cooldown,
        "is_alive": agent.is_alive,
    }


def _genome_payload(genome: Genome) -> dict[str, Any]:
    genes = [link.gene for link in genome.gene_links]
    gene_ids = {gene.id for gene in genes}
    edges = [edge for gene in genes for edge in gene.outgoing_edges if edge.target_id in gene_ids]
    return {
        "id": genome.id,
        "name": genome.name,
        "genes": [_gene_payload(gene) for gene in genes],
        "edges": [_gene_edge_payload(edge) for edge in edges],
    }


def _gene_payload(gene) -> dict[str, Any]:
    data = gene_to_dict(gene)
    return {
        "id": data["id"],
        "name": data["name"],
        "effect_type": data["effect_type"],
        "threshold": data["threshold"],
        "weight": data["weight"],
        "default_active": data["default_active"],
    }


def _gene_edge_payload(edge) -> dict[str, Any]:
    data = gene_edge_to_dict(edge)
    return {
        "id": data["id"],
        "source": data["source"],
        "target": data["target"],
        "weight": data["weight"],
    }
