import uuid
from dataclasses import dataclass

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

        existing_stmt = select(Simulation).where(
            Simulation.user_id == user_id,
            Simulation.name == self.DEMO_NAME,
        )
        existing_result = await db.execute(existing_stmt)
        existing_demo = existing_result.scalar_one_or_none()

        if existing_demo is not None:
            return

        template_stmt = (
            select(GenomeTemplate)
            .where(
                GenomeTemplate.user_id == user_id,
                GenomeTemplate.is_builtin == True,  # noqa: E712
                GenomeTemplate.name.in_(
                    [
                        "Травоядный собиратель",
                        "Хищник-охотник",
                        "Осторожный кочевник",
                        "Всеядный оппортунист",
                    ]
                ),
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
            name=self.DEMO_NAME,
            status="draft",
            tick=0,
        )
        db.add(simulation)
        await db.flush()

        territory_id_by_key: dict[str, int] = {}

        for territory_spec in self.TERRITORIES:
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

        for edge_spec in self.EDGES:
            db.add(
                TerritoryEdge(
                    simulation_id=simulation.id,
                    source_territory_id=territory_id_by_key[edge_spec.source_key],
                    target_territory_id=territory_id_by_key[edge_spec.target_key],
                    movement_cost=edge_spec.movement_cost,
                )
            )

        for agent_spec in self.AGENTS:
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
