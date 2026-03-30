from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.gene import Gene
from app.models.gene_edge import GeneEdge
from app.models.gene_state import GeneState
from app.models.simulation import Simulation


class EnginePersister:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def persist_state(self, simulation: Simulation, state: dict[str, Any]) -> None:
        simulation.tick = state["tick"]

        territories_by_id = {territory.id: territory for territory in simulation.territories}

        for territory_data in state["territories"]:
            territory_id = int(territory_data["id"])
            territory = territories_by_id[territory_id]
            territory.food = territory_data["food"]
            territory.temperature = territory_data["temperature"]
            territory.food_regen_per_tick = territory_data["food_regen_per_tick"]
            territory.food_capacity = territory_data["food_capacity"]

        existing_agents_by_id = {agent.id: agent for agent in simulation.agents}

        state_agent_ids = {agent_data["id"] for agent_data in state["agents"]}

        # удалить агентов, которых больше нет в state
        for existing_agent in list(simulation.agents):
            if existing_agent.id not in state_agent_ids:
                await self.db.delete(existing_agent)

        await self.db.flush()

        existing_agents_by_id = {agent.id: agent for agent in simulation.agents}

        for agent_data in state["agents"]:
            agent_id = agent_data["id"]

            if agent_id not in existing_agents_by_id:
                new_agent = Agent(
                    id=agent_id,
                    simulation_id=simulation.id,
                    territory_id=int(agent_data["location"]),
                    hunger=agent_data["hunger"],
                    hp=agent_data["hp"],
                    base_strength=agent_data["base_strength"],
                    base_defense=agent_data["base_defense"],
                    sex=agent_data["sex"],
                    pregnant=agent_data["pregnant"],
                    ticks_to_birth=agent_data["ticks_to_birth"],
                    hunt_cooldown=agent_data.get("hunt_cooldown", 0),
                    father_id=(
                        agent_data["father_id"] if agent_data["father_id"] is not None else None
                    ),
                    base_temp_pref=agent_data["base_temp_pref"],
                    satisfaction=agent_data["satisfaction"],
                    alive=agent_data["alive"],
                )
                self.db.add(new_agent)
                await self.db.flush()
                existing_agents_by_id[new_agent.id] = new_agent

            agent = existing_agents_by_id[agent_id]

            agent.territory_id = int(agent_data["location"])
            agent.hunger = agent_data["hunger"]
            agent.hp = agent_data["hp"]
            agent.base_strength = agent_data["base_strength"]
            agent.base_defense = agent_data["base_defense"]
            agent.sex = agent_data["sex"]
            agent.pregnant = agent_data["pregnant"]
            agent.ticks_to_birth = agent_data["ticks_to_birth"]
            agent.hunt_cooldown = agent_data.get("hunt_cooldown", 0)
            agent.father_id = (
                agent_data["father_id"] if agent_data["father_id"] is not None else None
            )
            agent.base_temp_pref = agent_data["base_temp_pref"]
            agent.satisfaction = agent_data["satisfaction"]
            agent.alive = agent_data["alive"]

            # Полностью пересобираем геном и gene_state этого агента.
            # Для первой версии это проще и надёжнее, чем patch update.
            await self.db.execute(delete(GeneState).where(GeneState.agent_id == agent.id))
            await self.db.execute(delete(GeneEdge).where(GeneEdge.agent_id == agent.id))
            await self.db.execute(delete(Gene).where(Gene.agent_id == agent.id))
            await self.db.flush()

            for gene_data in agent_data["genes"]:
                self.db.add(
                    Gene(
                        id=int(gene_data["id"]),
                        agent_id=agent.id,
                        name=gene_data["name"],
                        effect_type=gene_data["effect_type"],
                        chromosome_id=gene_data["chromosome_id"],
                        position=gene_data["position"],
                        default_active=gene_data["default_active"],
                        threshold=gene_data["threshold"],
                    )
                )

            await self.db.flush()

            for edge_data in agent_data["gene_edges"]:
                self.db.add(
                    GeneEdge(
                        agent_id=agent.id,
                        source_gene_id=str(edge_data["source_gene_id"]),
                        target_gene_id=str(edge_data["target_gene_id"]),
                        weight=edge_data["weight"],
                    )
                )

            for gene_state_data in agent_data["gene_states"]:
                self.db.add(
                    GeneState(
                        agent_id=agent.id,
                        gene_id=str(gene_state_data["gene_id"]),
                        is_active=gene_state_data["is_active"],
                    )
                )

        await self.db.commit()
        await self.db.refresh(simulation)
