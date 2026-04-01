import uuid
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import Agent
from app.models.gene import Gene
from app.models.gene_edge import GeneEdge
from app.models.gene_state import GeneState
from app.models.genome_template import GenomeTemplate
from app.models.simulation import Simulation
from app.models.territory import Territory
from app.models.territory_edge import TerritoryEdge
from app.services.builtin_genome_template_seeder import BuiltinGenomeTemplateSeeder

SimulationPresetName = Literal[
    "base_demo",
    "food_scarcity",
    "cold_climate",
    "predator_dominance",
    "high_density",
    "social_tolerance",
]


@dataclass(frozen=True)
class DemoTerritorySpec:
    key: str
    food: float
    temperature: float
    food_regen_per_tick: float
    food_capacity: float
    x: int
    y: int


@dataclass(frozen=True)
class DemoEdgeSpec:
    source_key: str
    target_key: str
    movement_cost: float


@dataclass(frozen=True)
class DemoAgentSpec:
    template_name: str
    territory_key: str
    hunger: int
    hp: int
    base_strength: int
    base_defense: int
    sex: str
    base_temp_pref: float
    satisfaction: float = 1.0
    alive: bool = True


class DemoSimulationSeeder:
    PRESET_TITLES: dict[str, str] = {
        "base_demo": "Сценарий: базовый",
        "food_scarcity": "Сценарий: дефицит пищи",
        "cold_climate": "Сценарий: холодный климат",
        "predator_dominance": "Сценарий: доминирование хищников",
        "high_density": "Сценарий: высокая плотность",
        "social_tolerance": "Сценарий: социальная терпимость",
    }

    DEMO_NAME = "Демо: хищники и травоядные"

    TERRITORIES: tuple[DemoTerritorySpec, ...] = (
        DemoTerritorySpec(
            key="meadow",
            food=12.0,
            temperature=20.0,
            food_regen_per_tick=2.0,
            food_capacity=12.0,
            x=120,
            y=160,
        ),
        DemoTerritorySpec(
            key="contested",
            food=1.0,
            temperature=19.0,
            food_regen_per_tick=0.5,
            food_capacity=6.0,
            x=420,
            y=160,
        ),
        DemoTerritorySpec(
            key="warm",
            food=7.0,
            temperature=26.0,
            food_regen_per_tick=1.5,
            food_capacity=10.0,
            x=720,
            y=120,
        ),
        DemoTerritorySpec(
            key="cold",
            food=4.0,
            temperature=9.0,
            food_regen_per_tick=1.0,
            food_capacity=8.0,
            x=420,
            y=420,
        ),
    )

    EDGES: tuple[DemoEdgeSpec, ...] = (
        DemoEdgeSpec(source_key="meadow", target_key="contested", movement_cost=1.0),
        DemoEdgeSpec(source_key="contested", target_key="warm", movement_cost=1.0),
        DemoEdgeSpec(source_key="contested", target_key="cold", movement_cost=1.0),
        DemoEdgeSpec(source_key="meadow", target_key="cold", movement_cost=1.0),
    )

    AGENTS: tuple[DemoAgentSpec, ...] = (
        DemoAgentSpec(
            template_name="Травоядный собиратель",
            territory_key="meadow",
            hunger=1,
            hp=5,
            base_strength=2,
            base_defense=2,
            sex="female",
            base_temp_pref=20.0,
        ),
        DemoAgentSpec(
            template_name="Травоядный собиратель",
            territory_key="meadow",
            hunger=2,
            hp=5,
            base_strength=2,
            base_defense=2,
            sex="male",
            base_temp_pref=20.0,
        ),
        DemoAgentSpec(
            template_name="Травоядный собиратель",
            territory_key="contested",
            hunger=2,
            hp=5,
            base_strength=2,
            base_defense=2,
            sex="female",
            base_temp_pref=19.0,
        ),
        DemoAgentSpec(
            template_name="Хищник-охотник",
            territory_key="contested",
            hunger=4,
            hp=5,
            base_strength=5,
            base_defense=3,
            sex="male",
            base_temp_pref=19.0,
        ),
        DemoAgentSpec(
            template_name="Хищник-охотник",
            territory_key="warm",
            hunger=3,
            hp=5,
            base_strength=4,
            base_defense=3,
            sex="female",
            base_temp_pref=24.0,
        ),
        DemoAgentSpec(
            template_name="Осторожный кочевник",
            territory_key="cold",
            hunger=1,
            hp=5,
            base_strength=2,
            base_defense=3,
            sex="male",
            base_temp_pref=11.0,
        ),
        DemoAgentSpec(
            template_name="Всеядный оппортунист",
            territory_key="warm",
            hunger=2,
            hp=5,
            base_strength=3,
            base_defense=3,
            sex="female",
            base_temp_pref=25.0,
        ),
    )

    async def seed_for_user(self, db: AsyncSession, user_id: int) -> None:
        await BuiltinGenomeTemplateSeeder().seed_for_user(db, user_id)

        existing_stmt = (
            select(Simulation.id)
            .where(
                Simulation.user_id == user_id,
                Simulation.name == self.PRESET_TITLES["base_demo"],
            )
            .limit(1)
        )
        existing_result = await db.execute(existing_stmt)
        existing_demo_id = existing_result.scalar_one_or_none()

        if existing_demo_id is not None:
            return

        await self.create_preset_simulation(
            db=db,
            user_id=user_id,
            preset="base_demo",
            custom_name=None,
        )

    async def _create_agent_from_template(
        self,
        db: AsyncSession,
        simulation_id: int,
        territory_id: int,
        template: GenomeTemplate,
        hunger: int,
        hp: int,
        base_strength: int,
        base_defense: int,
        sex: str,
        base_temp_pref: float,
        satisfaction: float,
        alive: bool,
    ) -> None:
        agent = Agent(
            id=str(uuid.uuid4()),
            simulation_id=simulation_id,
            territory_id=territory_id,
            hunger=hunger,
            hp=hp,
            base_strength=base_strength,
            base_defense=base_defense,
            sex=sex,
            species_group=template.species_group,
            pregnant=False,
            ticks_to_birth=0,
            father_id=None,
            hunt_cooldown=0,
            base_temp_pref=base_temp_pref,
            satisfaction=satisfaction,
            alive=alive,
        )
        db.add(agent)
        await db.flush()

        gene_id_map: dict[int, int] = {}

        for template_gene in template.genes:
            agent_gene = Gene(
                agent_id=agent.id,
                name=template_gene.name,
                effect_type=template_gene.effect_type,
                chromosome_id=template_gene.chromosome_id,
                position=template_gene.position,
                default_active=template_gene.default_active,
                threshold=template_gene.threshold,
            )
            db.add(agent_gene)
            await db.flush()
            gene_id_map[template_gene.id] = agent_gene.id

        for template_edge in template.edges:
            source_gene_id = gene_id_map.get(template_edge.source_gene_id)
            target_gene_id = gene_id_map.get(template_edge.target_gene_id)

            if source_gene_id is None or target_gene_id is None:
                continue

            db.add(
                GeneEdge(
                    agent_id=agent.id,
                    source_gene_id=str(source_gene_id),
                    target_gene_id=str(target_gene_id),
                    weight=template_edge.weight,
                )
            )

        for template_state in template.gene_states:
            mapped_gene_id = gene_id_map.get(template_state.gene_id)
            if mapped_gene_id is None:
                continue

            db.add(
                GeneState(
                    agent_id=agent.id,
                    gene_id=str(mapped_gene_id),
                    is_active=template_state.is_active,
                )
            )

    async def create_preset_simulation(
        self,
        db: AsyncSession,
        user_id: int,
        preset: SimulationPresetName,
        custom_name: str | None = None,
    ) -> Simulation:
        await BuiltinGenomeTemplateSeeder().seed_for_user(db, user_id)

        template_stmt = (
            select(GenomeTemplate)
            .where(
                GenomeTemplate.user_id == user_id,
                GenomeTemplate.is_builtin == True,  # noqa: E712
            )
            .options(
                selectinload(GenomeTemplate.genes),
                selectinload(GenomeTemplate.edges),
                selectinload(GenomeTemplate.gene_states),
            )
        )
        template_result = await db.execute(template_stmt)
        templates = {template.name: template for template in template_result.scalars().all()}

        simulation = Simulation(
            user_id=user_id,
            name=custom_name or self.PRESET_TITLES[preset],
            status="draft",
            tick=0,
        )
        db.add(simulation)
        await db.flush()

        territory_specs = self._build_territories_for_preset(preset)
        edge_specs = self._build_edges_for_preset(preset)
        agent_specs = self._build_agents_for_preset(preset)

        territory_id_by_key: dict[str, int] = {}

        for territory_spec in territory_specs:
            territory = Territory(
                simulation_id=simulation.id,
                food=territory_spec.food,
                temperature=territory_spec.temperature,
                food_regen_per_tick=territory_spec.food_regen_per_tick,
                food_capacity=territory_spec.food_capacity,
                x=territory_spec.x,
                y=territory_spec.y,
            )
            db.add(territory)
            await db.flush()
            territory_id_by_key[territory_spec.key] = territory.id

        for edge_spec in edge_specs:
            db.add(
                TerritoryEdge(
                    simulation_id=simulation.id,
                    source_territory_id=territory_id_by_key[edge_spec.source_key],
                    target_territory_id=territory_id_by_key[edge_spec.target_key],
                    movement_cost=edge_spec.movement_cost,
                )
            )

        for agent_spec in agent_specs:
            template = templates.get(agent_spec.template_name)
            if template is None:
                continue

            territory_id = territory_id_by_key[agent_spec.territory_key]

            await self._create_agent_from_template(
                db=db,
                simulation_id=simulation.id,
                territory_id=territory_id,
                template=template,
                hunger=agent_spec.hunger,
                hp=agent_spec.hp,
                base_strength=agent_spec.base_strength,
                base_defense=agent_spec.base_defense,
                sex=agent_spec.sex,
                base_temp_pref=agent_spec.base_temp_pref,
                satisfaction=agent_spec.satisfaction,
                alive=agent_spec.alive,
            )

        await db.commit()
        return simulation

    def _build_territories_for_preset(
        self,
        preset: SimulationPresetName,
    ) -> tuple[DemoTerritorySpec, ...]:
        if preset == "food_scarcity":
            return (
                DemoTerritorySpec("meadow", 3.0, 20.0, 0.4, 5.0, 120, 160),
                DemoTerritorySpec("contested", 0.0, 19.0, 0.2, 3.0, 420, 160),
                DemoTerritorySpec("warm", 2.0, 26.0, 0.3, 4.0, 720, 120),
                DemoTerritorySpec("cold", 1.0, 9.0, 0.3, 4.0, 420, 420),
            )

        if preset == "cold_climate":
            return (
                DemoTerritorySpec("meadow", 8.0, 8.0, 1.2, 10.0, 120, 160),
                DemoTerritorySpec("contested", 5.0, 5.0, 0.8, 7.0, 420, 160),
                DemoTerritorySpec("warm", 4.0, 12.0, 0.9, 6.0, 720, 120),
                DemoTerritorySpec("cold", 5.0, 2.0, 1.0, 7.0, 420, 420),
            )

        return self.TERRITORIES

    def _build_edges_for_preset(
        self,
        preset: SimulationPresetName,
    ) -> tuple[DemoEdgeSpec, ...]:
        if preset == "high_density":
            return (
                DemoEdgeSpec("meadow", "contested", 1.0),
                DemoEdgeSpec("contested", "warm", 1.0),
                DemoEdgeSpec("contested", "cold", 1.0),
                DemoEdgeSpec("meadow", "cold", 1.0),
                DemoEdgeSpec("meadow", "warm", 1.0),
            )

        return self.EDGES

    def _build_agents_for_preset(
        self,
        preset: SimulationPresetName,
    ) -> tuple[DemoAgentSpec, ...]:
        if preset == "predator_dominance":
            return (
                DemoAgentSpec("Хищник-охотник", "contested", 4, 5, 5, 3, "male", 19.0),
                DemoAgentSpec("Хищник-охотник", "contested", 3, 5, 4, 3, "female", 19.0),
                DemoAgentSpec("Хищник-охотник", "warm", 3, 5, 4, 3, "male", 24.0),
                DemoAgentSpec("Травоядный собиратель", "meadow", 1, 5, 2, 2, "female", 20.0),
                DemoAgentSpec("Травоядный собиратель", "cold", 2, 5, 2, 2, "male", 10.0),
            )

        if preset == "high_density":
            return (
                DemoAgentSpec("Травоядный собиратель", "contested", 1, 5, 2, 2, "female", 19.0),
                DemoAgentSpec("Травоядный собиратель", "contested", 2, 5, 2, 2, "male", 19.0),
                DemoAgentSpec("Всеядный оппортунист", "contested", 2, 5, 3, 3, "female", 19.0),
                DemoAgentSpec("Всеядный оппортунист", "contested", 2, 5, 3, 3, "male", 19.0),
                DemoAgentSpec("Осторожный кочевник", "contested", 1, 5, 2, 3, "male", 19.0),
                DemoAgentSpec("Хищник-охотник", "warm", 4, 5, 5, 3, "male", 24.0),
            )

        if preset == "social_tolerance":
            return (
                DemoAgentSpec("Травоядный собиратель", "meadow", 1, 5, 2, 2, "female", 20.0),
                DemoAgentSpec("Травоядный собиратель", "meadow", 2, 5, 2, 2, "male", 20.0),
                DemoAgentSpec("Всеядный оппортунист", "meadow", 2, 5, 3, 3, "female", 20.0),
                DemoAgentSpec("Всеядный оппортунист", "contested", 2, 5, 3, 3, "male", 19.0),
                DemoAgentSpec("Осторожный кочевник", "cold", 1, 5, 2, 3, "male", 11.0),
            )

        return self.AGENTS
