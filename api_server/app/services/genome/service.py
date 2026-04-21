from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.mappers.genome import genome_list_item_to_dict, genome_to_dict
from app.models import Gene, GeneEdge, Genome
from app.models.relations.genome_agent import GenomeAgentRelation
from app.models.relations.genome_gene import GenomeGeneRelation
from app.models.relations.genome_user import GenomeUserRelation
from app.models.relations.simulation_agent import SimulationAgentRelation
from app.repositories.genome.genome import GenomeRepository
from app.schemas import GeneCreate, GeneEdgeCreate, GenomeCreate, Position
from app.services.scenario import ScenarioService
from app.services.simulation.runtime_orchestrator import SimulationRuntimeOrchestrator


class GenomeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.genomes = GenomeRepository(session)
        self.runtime_orchestrator = SimulationRuntimeOrchestrator(session)

    async def list_by_user(self, user_id: int) -> list[dict]:
        await ScenarioService(self.session).ensure_template_genomes()
        await self.session.commit()
        rows = await self.genomes.list_by_user(user_id)
        return [genome_list_item_to_dict(genome, owner_id) for genome, owner_id in rows]

    async def available_for_user(self, user_id: int) -> list[dict]:
        await ScenarioService(self.session).ensure_template_genomes()
        await self.session.commit()
        genomes = await self.genomes.available_for_user(user_id)
        return [
            {
                "id": genome.id,
                "name": genome.name,
                "is_template": genome.is_template,
                "template_key": genome_list_item_to_dict(genome).get("template_key"),
            }
            for genome in genomes
        ]

    async def create(self, user_id: int, payload: GenomeCreate) -> None:
        genome = Genome(name=payload.name)
        self.session.add(genome)
        await self.session.flush()
        self.session.add(GenomeUserRelation(user_id=user_id, genome_id=genome.id))
        await self.session.commit()

    async def get(self, genome_id: int, user_id: int) -> dict:
        genome = await self.genomes.get_available_with_graph(genome_id, user_id)
        if genome is None:
            raise HTTPException(status_code=404, detail="Genome not found")
        return genome_to_dict(genome)

    async def create_gene(self, genome_id: int, user_id: int, payload: GeneCreate) -> None:
        genome = await self.genomes.get_owned(genome_id, user_id)
        if genome is None:
            raise HTTPException(status_code=404, detail="Genome not found")
        await self._mark_related_simulations_stale(genome_id, user_id)

        gene = Gene(
            name=(payload.name or payload.effect_type.value),
            effect_type=payload.effect_type.value,
            threshold=payload.threshold,
            weight=payload.weight,
            x=payload.position.x,
            y=payload.position.y,
            default_active=payload.default_active,
        )
        self.session.add(gene)
        await self.session.flush()
        self.session.add(GenomeGeneRelation(genome_id=genome.id, gene_id=gene.id))
        await self.session.commit()

    async def update_gene(
        self,
        genome_id: int,
        gene_id: int,
        user_id: int,
        payload: GeneCreate,
    ) -> None:
        gene = await self._get_owned_gene(genome_id, gene_id, user_id)
        await self._mark_related_simulations_stale(genome_id, user_id)
        gene.name = payload.name or payload.effect_type.value
        gene.effect_type = payload.effect_type.value
        gene.threshold = payload.threshold
        gene.weight = payload.weight
        gene.x = payload.position.x
        gene.y = payload.position.y
        gene.default_active = payload.default_active
        await self.session.commit()

    async def delete_gene(self, genome_id: int, gene_id: int, user_id: int) -> None:
        gene = await self._get_owned_gene(genome_id, gene_id, user_id)
        await self._mark_related_simulations_stale(genome_id, user_id)
        await self.session.delete(gene)
        await self.session.commit()

    async def create_edge(self, genome_id: int, user_id: int, payload: GeneEdgeCreate) -> None:
        genome = await self.genomes.get_owned(genome_id, user_id)
        if genome is None:
            raise HTTPException(status_code=404, detail="Genome not found")

        gene_ids = {link.gene_id for link in genome.gene_links}
        if payload.source not in gene_ids or payload.target not in gene_ids:
            raise HTTPException(
                status_code=400,
                detail="Edge genes must belong to this genome",
            )
        if payload.source == payload.target:
            raise HTTPException(status_code=400, detail="Edge cannot point to itself")
        await self._mark_related_simulations_stale(genome_id, user_id)

        self.session.add(
            GeneEdge(
                source_id=payload.source,
                target_id=payload.target,
                weight=payload.weight,
            )
        )
        await self.session.commit()

    async def update_gene_position(
        self,
        genome_id: int,
        gene_id: int,
        user_id: int,
        position: Position,
    ) -> None:
        gene = await self._get_owned_gene(genome_id, gene_id, user_id)
        gene.x = position.x
        gene.y = position.y
        await self.session.commit()

    async def _get_owned_gene(self, genome_id: int, gene_id: int, user_id: int) -> Gene:
        genome = await self.genomes.get_owned(genome_id, user_id)
        if genome is None:
            raise HTTPException(status_code=404, detail="Genome not found")

        gene_ids = {link.gene_id for link in genome.gene_links}
        if gene_id not in gene_ids:
            raise HTTPException(status_code=404, detail="Gene not found")

        gene = await self.session.get(Gene, gene_id)
        if gene is None:
            raise HTTPException(status_code=404, detail="Gene not found")
        return gene

    async def _mark_related_simulations_stale(self, genome_id: int, user_id: int) -> None:
        simulation_ids = (
            await self.session.scalars(
                select(SimulationAgentRelation.simulation_id)
                .join(
                    GenomeAgentRelation,
                    GenomeAgentRelation.agent_id == SimulationAgentRelation.agent_id,
                )
                .where(GenomeAgentRelation.genome_id == genome_id)
                .distinct()
            )
        ).all()
        for simulation_id in simulation_ids:
            await self.runtime_orchestrator.mark_runtime_stale(user_id, simulation_id)
