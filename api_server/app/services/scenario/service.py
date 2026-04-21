from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Agent, Gene, GeneEdge, Genome, Simulation, Territory, TerritoryEdge
from app.models.relations.genome_agent import GenomeAgentRelation
from app.models.relations.genome_gene import GenomeGeneRelation
from app.models.relations.simulation_agent import SimulationAgentRelation
from app.models.relations.simulation_territory import SimulationTerritoryRelation
from app.models.relations.simulation_user import SimulationUserRelation
from app.models.relations.territory_agent import TerritoryAgentRelation

from .definitions import SCENARIOS, TEMPLATE_GENOMES, ScenarioDefinition, TemplateGenomeDefinition


class ScenarioService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_scenarios(self) -> list[dict]:
        return [
            {
                "key": scenario.key,
                "name": scenario.name,
                "description": scenario.description,
            }
            for scenario in SCENARIOS
        ]

    async def create_from_scenario(self, user_id: int, scenario_key: str) -> int:
        scenario = self._get_scenario(scenario_key)
        templates = await self.ensure_template_genomes()

        simulation = Simulation(name=scenario.name)
        self.session.add(simulation)
        await self.session.flush()
        self.session.add(SimulationUserRelation(user_id=user_id, simulation_id=simulation.id))

        territories_by_key: dict[str, Territory] = {}
        for territory_definition in scenario.territories:
            territory = Territory(
                food=territory_definition.food,
                food_capacity=territory_definition.food_capacity,
                food_regen_per_tick=territory_definition.food_regen_per_tick,
                temperature=territory_definition.temperature,
                x=territory_definition.x,
                y=territory_definition.y,
            )
            self.session.add(territory)
            await self.session.flush()
            self.session.add(
                SimulationTerritoryRelation(
                    simulation_id=simulation.id,
                    territory_id=territory.id,
                )
            )
            territories_by_key[territory_definition.key] = territory

        for source_key, target_key, weight in scenario.edges:
            source = territories_by_key[source_key]
            target = territories_by_key[target_key]
            self.session.add(
                TerritoryEdge(source_id=source.id, target_id=target.id, movement_cost=weight)
            )
            self.session.add(
                TerritoryEdge(source_id=target.id, target_id=source.id, movement_cost=weight)
            )

        for group in scenario.agent_groups:
            genome = templates[group.genome_key]
            territory = territories_by_key[group.territory_key]
            for index in range(group.count):
                sex = group.sex_pattern[index % len(group.sex_pattern)]
                agent = Agent(
                    sex=sex,
                    hunger=group.hunger,
                    hp=group.hp,
                    strength=group.strength,
                    defense=group.defense,
                    temp_pref=group.temp_pref,
                    satisfaction=group.satisfaction,
                )
                self.session.add(agent)
                await self.session.flush()
                self.session.add(
                    SimulationAgentRelation(simulation_id=simulation.id, agent_id=agent.id)
                )
                self.session.add(
                    TerritoryAgentRelation(territory_id=territory.id, agent_id=agent.id)
                )
                self.session.add(GenomeAgentRelation(genome_id=genome.id, agent_id=agent.id))

        await self.session.commit()
        return simulation.id

    async def ensure_template_genomes(self) -> dict[str, Genome]:
        templates: dict[str, Genome] = {}
        for definition in TEMPLATE_GENOMES:
            templates[definition.key] = await self._ensure_template_genome(definition)
        await self.session.flush()
        return templates

    async def _ensure_template_genome(self, definition: TemplateGenomeDefinition) -> Genome:
        existing = await self.session.scalar(
            select(Genome).where(
                Genome.name == definition.name,
                Genome.is_template.is_(True),
            )
        )
        if existing is not None:
            return existing

        genome = Genome(
            name=definition.name,
            description=definition.description,
            is_template=True,
        )
        self.session.add(genome)
        await self.session.flush()

        genes_by_key: dict[str, Gene] = {}
        for gene_definition in definition.genes:
            gene = Gene(
                name=gene_definition.name,
                effect_type=gene_definition.effect_type,
                threshold=gene_definition.threshold,
                weight=gene_definition.weight,
                x=gene_definition.x,
                y=gene_definition.y,
                default_active=gene_definition.default_active,
            )
            self.session.add(gene)
            await self.session.flush()
            self.session.add(GenomeGeneRelation(genome_id=genome.id, gene_id=gene.id))
            genes_by_key[gene_definition.key] = gene

        for source_key, target_key, weight in definition.edges:
            self.session.add(
                GeneEdge(
                    source_id=genes_by_key[source_key].id,
                    target_id=genes_by_key[target_key].id,
                    weight=weight,
                )
            )

        return genome

    def _get_scenario(self, scenario_key: str) -> ScenarioDefinition:
        for scenario in SCENARIOS:
            if scenario.key == scenario_key:
                return scenario
        raise HTTPException(status_code=404, detail="Scenario not found")
