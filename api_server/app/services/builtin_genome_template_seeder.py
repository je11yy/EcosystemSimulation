from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.genome_template import GenomeTemplate
from app.models.genome_template_edge import GenomeTemplateEdge
from app.models.genome_template_gene import GenomeTemplateGene
from app.models.genome_template_gene_state import GenomeTemplateGeneState
from simulation_core.agents.genome.effect_type import GeneEffectType


@dataclass(frozen=True)
class BuiltinGeneSpec:
    name: str
    effect_type: GeneEffectType
    chromosome_id: str
    position: float
    threshold: float
    x: int
    y: int
    default_active: bool = True


@dataclass(frozen=True)
class BuiltinEdgeSpec:
    source_effect: GeneEffectType
    target_effect: GeneEffectType
    weight: float


@dataclass(frozen=True)
class BuiltinTemplateSpec:
    name: str
    description: str
    species_group: str
    base_predation_drive: float
    genes: tuple[BuiltinGeneSpec, ...]
    edges: tuple[BuiltinEdgeSpec, ...]


BUILTIN_TEMPLATES: tuple[BuiltinTemplateSpec, ...] = (
    BuiltinTemplateSpec(
        name="Травоядный собиратель",
        description=(
            "Спокойный встроенный шаблон для тестов: делает ставку на "
            "локальное питание, комфорт среды и размножение."
        ),
        species_group="demo_herbivore",
        base_predation_drive=0.0,
        genes=(
            BuiltinGeneSpec(
                name="Пищевой драйв",
                effect_type=GeneEffectType.HUNGER_DRIVE,
                chromosome_id="chr1",
                position=1.0,
                threshold=0.2,
                x=120,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Пищевой оппортунизм",
                effect_type=GeneEffectType.FOOD_OPPORTUNISM,
                chromosome_id="chr1",
                position=2.0,
                threshold=0.1,
                x=120,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Родительский вклад",
                effect_type=GeneEffectType.PARENTAL_INVESTMENT,
                chromosome_id="chr2",
                position=4.0,
                threshold=0.1,
                x=360,
                y=460,
            ),
            BuiltinGeneSpec(
                name="Привязанность к территории",
                effect_type=GeneEffectType.SITE_FIDELITY,
                chromosome_id="chr1",
                position=3.0,
                threshold=0.0,
                x=120,
                y=340,
            ),
            BuiltinGeneSpec(
                name="Драйв размножения",
                effect_type=GeneEffectType.REPRODUCTION_DRIVE,
                chromosome_id="chr2",
                position=1.0,
                threshold=0.1,
                x=360,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Социальная терпимость",
                effect_type=GeneEffectType.SOCIAL_TOLERANCE,
                chromosome_id="chr2",
                position=2.0,
                threshold=0.0,
                x=360,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Удовлетворённость средой",
                effect_type=GeneEffectType.HABITAT_SATISFACTION,
                chromosome_id="chr2",
                position=3.0,
                threshold=0.0,
                x=360,
                y=340,
            ),
        ),
        edges=(
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.HUNGER_DRIVE,
                target_effect=GeneEffectType.FOOD_OPPORTUNISM,
                weight=0.8,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.FOOD_OPPORTUNISM,
                target_effect=GeneEffectType.SITE_FIDELITY,
                weight=0.2,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.SITE_FIDELITY,
                target_effect=GeneEffectType.REPRODUCTION_DRIVE,
                weight=0.3,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.HABITAT_SATISFACTION,
                target_effect=GeneEffectType.SITE_FIDELITY,
                weight=0.4,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.REPRODUCTION_DRIVE,
                target_effect=GeneEffectType.PARENTAL_INVESTMENT,
                weight=0.5,
            ),
        ),
    ),
    BuiltinTemplateSpec(
        name="Хищник-охотник",
        description=(
            "Встроенный шаблон для тестов хищничества: высокий predation drive, "
            "агрессия и переваривание мясной пищи."
        ),
        species_group="demo_predator",
        base_predation_drive=1.0,
        genes=(
            BuiltinGeneSpec(
                name="Пищевой драйв",
                effect_type=GeneEffectType.HUNGER_DRIVE,
                chromosome_id="chr1",
                position=1.0,
                threshold=0.2,
                x=120,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Драйв расселения",
                effect_type=GeneEffectType.DISPERSAL_DRIVE,
                chromosome_id="chr1",
                position=2.0,
                threshold=0.0,
                x=120,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Агрессия",
                effect_type=GeneEffectType.AGGRESSION_DRIVE,
                chromosome_id="chr1",
                position=3.0,
                threshold=0.0,
                x=120,
                y=340,
            ),
            BuiltinGeneSpec(
                name="Драйв хищничества",
                effect_type=GeneEffectType.PREDATION_DRIVE,
                chromosome_id="chr2",
                position=1.0,
                threshold=0.1,
                x=360,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Плотоядное пищеварение",
                effect_type=GeneEffectType.CARNIVORE_DIGESTION,
                chromosome_id="chr2",
                position=2.0,
                threshold=0.0,
                x=360,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Оборонительная реакция",
                effect_type=GeneEffectType.DEFENSE_RESPONSE,
                chromosome_id="chr2",
                position=3.0,
                threshold=0.0,
                x=360,
                y=340,
            ),
        ),
        edges=(
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.HUNGER_DRIVE,
                target_effect=GeneEffectType.PREDATION_DRIVE,
                weight=0.9,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.AGGRESSION_DRIVE,
                target_effect=GeneEffectType.PREDATION_DRIVE,
                weight=0.8,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.DISPERSAL_DRIVE,
                target_effect=GeneEffectType.PREDATION_DRIVE,
                weight=0.3,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.PREDATION_DRIVE,
                target_effect=GeneEffectType.CARNIVORE_DIGESTION,
                weight=0.7,
            ),
        ),
    ),
    BuiltinTemplateSpec(
        name="Осторожный кочевник",
        description=(
            "Встроенный шаблон для тестов перемещения: склонен к MOVE, избегает "
            "конфликтов и лучше переносит холод."
        ),
        species_group="demo_wanderer",
        base_predation_drive=0.0,
        genes=(
            BuiltinGeneSpec(
                name="Драйв расселения",
                effect_type=GeneEffectType.DISPERSAL_DRIVE,
                chromosome_id="chr1",
                position=1.0,
                threshold=0.0,
                x=120,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Рискованное движение",
                effect_type=GeneEffectType.RISK_MOVE,
                chromosome_id="chr1",
                position=2.0,
                threshold=0.0,
                x=120,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Избегание конфликта",
                effect_type=GeneEffectType.ESCAPE_RESPONSE,
                chromosome_id="chr1",
                position=3.0,
                threshold=0.0,
                x=120,
                y=340,
            ),
            BuiltinGeneSpec(
                name="Холодоустойчивость",
                effect_type=GeneEffectType.COLD_RESISTANCE,
                chromosome_id="chr2",
                position=1.0,
                threshold=0.0,
                x=360,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Избирательность партнёра",
                effect_type=GeneEffectType.MATE_SELECTIVITY,
                chromosome_id="chr2",
                position=2.0,
                threshold=0.2,
                x=360,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Социальная терпимость",
                effect_type=GeneEffectType.SOCIAL_TOLERANCE,
                chromosome_id="chr2",
                position=3.0,
                threshold=0.0,
                x=360,
                y=340,
            ),
        ),
        edges=(
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.DISPERSAL_DRIVE,
                target_effect=GeneEffectType.RISK_MOVE,
                weight=0.5,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.ESCAPE_RESPONSE,
                target_effect=GeneEffectType.DISPERSAL_DRIVE,
                weight=0.4,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.COLD_RESISTANCE,
                target_effect=GeneEffectType.DISPERSAL_DRIVE,
                weight=0.2,
            ),
        ),
    ),
    BuiltinTemplateSpec(
        name="Всеядный оппортунист",
        description=(
            "Встроенный компромиссный шаблон для тестов: ест доступную пищу, "
            "готов двигаться и неплохо переносит плотность."
        ),
        species_group="demo_omnivore",
        base_predation_drive=0.25,
        genes=(
            BuiltinGeneSpec(
                name="Пищевой драйв",
                effect_type=GeneEffectType.HUNGER_DRIVE,
                chromosome_id="chr1",
                position=1.0,
                threshold=0.1,
                x=120,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Пищевой оппортунизм",
                effect_type=GeneEffectType.FOOD_OPPORTUNISM,
                chromosome_id="chr1",
                position=2.0,
                threshold=0.0,
                x=120,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Рискованное движение",
                effect_type=GeneEffectType.RISK_MOVE,
                chromosome_id="chr1",
                position=3.0,
                threshold=0.0,
                x=120,
                y=340,
            ),
            BuiltinGeneSpec(
                name="Социальная терпимость",
                effect_type=GeneEffectType.SOCIAL_TOLERANCE,
                chromosome_id="chr2",
                position=1.0,
                threshold=0.0,
                x=360,
                y=100,
            ),
            BuiltinGeneSpec(
                name="Оборонительная реакция",
                effect_type=GeneEffectType.DEFENSE_RESPONSE,
                chromosome_id="chr2",
                position=2.0,
                threshold=0.0,
                x=360,
                y=220,
            ),
            BuiltinGeneSpec(
                name="Жароустойчивость",
                effect_type=GeneEffectType.HEAT_RESISTANCE,
                chromosome_id="chr2",
                position=3.0,
                threshold=0.0,
                x=360,
                y=340,
            ),
        ),
        edges=(
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.HUNGER_DRIVE,
                target_effect=GeneEffectType.FOOD_OPPORTUNISM,
                weight=0.7,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.RISK_MOVE,
                target_effect=GeneEffectType.FOOD_OPPORTUNISM,
                weight=0.3,
            ),
            BuiltinEdgeSpec(
                source_effect=GeneEffectType.SOCIAL_TOLERANCE,
                target_effect=GeneEffectType.DEFENSE_RESPONSE,
                weight=0.2,
            ),
        ),
    ),
)


class BuiltinGenomeTemplateSeeder:
    async def seed_for_user(self, db: AsyncSession, user_id: int) -> None:
        existing_stmt = select(GenomeTemplate.name).where(
            GenomeTemplate.user_id == user_id,
            GenomeTemplate.is_builtin == True,  # noqa: E712
        )
        existing_result = await db.execute(existing_stmt)
        existing_names = set(existing_result.scalars().all())

        created_any = False

        for spec in BUILTIN_TEMPLATES:
            if spec.name in existing_names:
                continue

            await self._create_template(db=db, user_id=user_id, spec=spec)
            created_any = True

        if created_any:
            await db.commit()

    async def _create_template(
        self,
        db: AsyncSession,
        user_id: int,
        spec: BuiltinTemplateSpec,
    ) -> None:
        template = GenomeTemplate(
            user_id=user_id,
            name=spec.name,
            description=spec.description,
            species_group=spec.species_group,
            is_builtin=True,
            base_predation_drive=spec.base_predation_drive,
        )
        db.add(template)
        await db.flush()

        genes = [
            GenomeTemplateGene(
                genome_template_id=template.id,
                name=gene_spec.name,
                effect_type=gene_spec.effect_type,
                chromosome_id=gene_spec.chromosome_id,
                position=gene_spec.position,
                default_active=gene_spec.default_active,
                threshold=gene_spec.threshold,
                x=gene_spec.x,
                y=gene_spec.y,
            )
            for gene_spec in spec.genes
        ]
        db.add_all(genes)
        await db.flush()

        gene_id_by_effect = {gene.effect_type: gene.id for gene in genes}

        states = [
            GenomeTemplateGeneState(
                genome_template_id=template.id,
                gene_id=gene.id,
                is_active=gene.default_active,
            )
            for gene in genes
        ]
        db.add_all(states)

        edges = self._build_edges(
            genome_template_id=template.id,
            edge_specs=spec.edges,
            gene_id_by_effect=gene_id_by_effect,
        )
        db.add_all(edges)

    def _build_edges(
        self,
        genome_template_id: int,
        edge_specs: Iterable[BuiltinEdgeSpec],
        gene_id_by_effect: dict[GeneEffectType, int],
    ) -> list[GenomeTemplateEdge]:
        edges: list[GenomeTemplateEdge] = []

        for edge_spec in edge_specs:
            source_gene_id = gene_id_by_effect.get(edge_spec.source_effect)
            target_gene_id = gene_id_by_effect.get(edge_spec.target_effect)

            if source_gene_id is None or target_gene_id is None:
                continue

            edges.append(
                GenomeTemplateEdge(
                    genome_template_id=genome_template_id,
                    source_gene_id=source_gene_id,
                    target_gene_id=target_gene_id,
                    weight=edge_spec.weight,
                )
            )

        return edges
