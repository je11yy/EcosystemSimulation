from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Agent, Gene, GeneEdge, Genome, SimulationLog
from app.models.relations.agent_parent import AgentParentRelation
from app.models.relations.genome_agent import GenomeAgentRelation
from app.models.relations.genome_gene import GenomeGeneRelation
from app.models.relations.simulation_agent import SimulationAgentRelation
from app.models.relations.territory_agent import TerritoryAgentRelation
from app.repositories.agent import AgentRepository
from app.repositories.simulation import SimulationRepository

MAX_GENE_NAME_LENGTH = 120


class RuntimeSnapshotPersister:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session)
        self.simulations = SimulationRepository(session)

    async def save_result(self, simulation_id: int, result: dict) -> None:
        tick = int(result["tick"])
        existing_log = await self.session.scalar(
            select(SimulationLog).where(
                SimulationLog.simulation_id == simulation_id,
                SimulationLog.tick == tick,
            )
        )
        if existing_log is not None:
            return

        self.session.add(
            SimulationLog(
                simulation_id=simulation_id,
                tick=tick,
                agent_decisions=self._decision_payloads(result.get("decisions", [])),
                step_result=result.get("step", {}),
                metrics=result.get("metrics", {}),
                events=self._event_payloads(result),
            )
        )

    async def apply_snapshot(self, user_id: int, snapshot: dict, result: dict) -> None:
        territories_by_id = {
            territory.id: territory
            for territory in (
                await self.simulations.get_details_parts(
                    snapshot["simulation_id"],
                    user_id,
                )
            )[1]
        }
        for territory_payload in snapshot.get("territories", []):
            territory = territories_by_id.get(territory_payload["id"])
            if territory is None:
                continue
            territory.food = territory_payload["food"]
            territory.temperature = territory_payload["temperature"]
            territory.food_regen_per_tick = territory_payload["food_regen_per_tick"]
            territory.food_capacity = territory_payload["food_capacity"]

        births_by_child_id = {int(birth["child_id"]): birth for birth in result.get("births", [])}
        parent_links: list[tuple[int, list[int]]] = []
        for agent_payload in snapshot.get("agents", []):
            agent = await self.agents.get_with_links(agent_payload["id"])
            if agent is None:
                if agent_payload["id"] in births_by_child_id:
                    parent_links.append(
                        await self._create_runtime_child_agent(
                            user_id=user_id,
                            simulation_id=snapshot["simulation_id"],
                            payload=agent_payload,
                            birth=births_by_child_id[agent_payload["id"]],
                        )
                    )
                continue
            self._apply_agent_payload(agent, agent_payload)

        await self.session.flush()
        await self._create_parent_links(parent_links)
        await self._sync_sequence("agents", "id")

    async def _create_parent_links(self, parent_links: list[tuple[int, list[int]]]) -> None:
        for child_id, parent_ids in parent_links:
            child = await self.session.get(Agent, child_id)
            if child is None:
                continue

            for parent_id in parent_ids:
                parent = await self.session.get(Agent, parent_id)
                if parent is None:
                    continue
                existing = await self.session.get(
                    AgentParentRelation,
                    {
                        "agent_id": child_id,
                        "parent_id": parent_id,
                    },
                )
                if existing is not None:
                    continue
                self.session.add(
                    AgentParentRelation(
                        agent_id=child_id,
                        parent_id=parent_id,
                    )
                )

    async def _create_runtime_child_agent(
        self,
        user_id: int,
        simulation_id: int,
        payload: dict,
        birth: dict,
    ) -> tuple[int, list[int]]:
        genome = await self._create_runtime_genome(
            user_id=user_id,
            child_id=payload["id"],
            genome_payload=payload.get("genome", {}),
        )
        agent = Agent(id=payload["id"], sex=payload["sex"])
        self._apply_agent_payload(agent, payload, update_location=False)
        self.session.add(agent)
        await self.session.flush()
        self.session.add(SimulationAgentRelation(agent_id=agent.id, simulation_id=simulation_id))
        self.session.add(
            TerritoryAgentRelation(agent_id=agent.id, territory_id=payload["territory_id"])
        )
        self.session.add(GenomeAgentRelation(agent_id=agent.id, genome_id=genome.id))

        parent_ids = [
            int(parent_id)
            for parent_id in (birth.get("parent_id"), birth.get("partner_id"))
            if parent_id is not None
        ]
        return agent.id, parent_ids

    async def _create_runtime_genome(
        self,
        user_id: int,
        child_id: int,
        genome_payload: dict,
    ) -> Genome:
        genome = Genome(
            name=f"Child {child_id} genome",
            description="Generated by simulation runtime",
            is_template=False,
        )
        self.session.add(genome)
        await self.session.flush()

        gene_id_map = {}
        for index, gene_payload in enumerate(genome_payload.get("genes", []), start=1):
            gene = Gene(
                name=_normalize_gene_name(gene_payload.get("name"), fallback=f"Gene {index}"),
                effect_type=gene_payload["effect_type"],
                threshold=gene_payload["threshold"],
                weight=gene_payload["weight"],
                default_active=gene_payload["default_active"],
                x=gene_payload.get("x", 100 + index * 32),
                y=gene_payload.get("y", 100 + index * 24),
            )
            self.session.add(gene)
            await self.session.flush()
            gene_id_map[gene_payload["id"]] = gene.id
            self.session.add(GenomeGeneRelation(genome_id=genome.id, gene_id=gene.id))

        for edge_payload in genome_payload.get("edges", []):
            source_id = gene_id_map.get(edge_payload["source"])
            target_id = gene_id_map.get(edge_payload["target"])
            if source_id is None or target_id is None:
                continue
            self.session.add(
                GeneEdge(
                    source_id=source_id,
                    target_id=target_id,
                    weight=edge_payload["weight"],
                )
            )

        return genome

    def _apply_agent_payload(
        self,
        agent: Agent,
        payload: dict,
        update_location: bool = True,
    ) -> None:
        agent.sex = payload["sex"]
        agent.hunger = payload["hunger"]
        agent.hp = payload["hp"]
        agent.strength = payload["strength"]
        agent.defense = payload["defense"]
        agent.temp_pref = payload["temp_pref"]
        agent.satisfaction = payload["satisfaction"]
        agent.is_pregnant = payload["pregnant"]
        agent.ticks_to_birth = payload["ticks_to_birth"]
        agent.hunt_cooldown = payload["hunt_cooldown"]
        agent.is_alive = payload["is_alive"]
        if (
            update_location
            and agent.id is not None
            and agent.territory_id != payload["territory_id"]
        ):
            self._move_agent(agent, payload["territory_id"])

    def _move_agent(self, agent: Agent, territory_id: int) -> None:
        if agent.territory_links:
            agent.territory_links[0].territory_id = territory_id
            return
        self.session.add(TerritoryAgentRelation(agent_id=agent.id, territory_id=territory_id))

    def _decision_payloads(self, decisions: list[dict]) -> list[dict]:
        payloads = []
        for decision in decisions:
            chosen = decision.get("chosen", {})
            payloads.append(
                {
                    "agent_id": int(decision["agent_id"]),
                    "action": chosen.get("type"),
                    "to_territory": chosen.get("to_territory"),
                    "partner_id": chosen.get("partner_id"),
                    "target_id": chosen.get("target_id"),
                    "metadata": {
                        "cost": decision.get("cost", {}),
                    },
                }
            )
        return payloads

    def _event_payloads(self, result: dict) -> dict:
        return {
            "applied_results": result.get("applied_results", []),
            "deaths": result.get("deaths", []),
            "births": result.get("births", []),
            "fights": result.get("fights", []),
            "hunts": result.get("hunts", []),
        }

    async def _sync_sequence(self, table: str, column: str) -> None:
        await self.session.execute(
            text(
                "SELECT setval("
                f"pg_get_serial_sequence('{table}', '{column}'), "
                f"COALESCE((SELECT MAX({column}) FROM {table}), 1)"
                ")"
            )
        )


def _normalize_gene_name(name: str | None, fallback: str) -> str:
    value = (name or fallback).strip()
    if len(value) <= MAX_GENE_NAME_LENGTH:
        return value
    return value[: MAX_GENE_NAME_LENGTH - 3].rstrip() + "..."
