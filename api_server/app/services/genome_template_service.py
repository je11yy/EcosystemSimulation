from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.genome_template_edge import GenomeTemplateEdge
from app.models.genome_template_gene import GenomeTemplateGene
from app.models.genome_template_gene_state import GenomeTemplateGeneState
from app.repositories.genome_template_repository import GenomeTemplateRepository
from app.schemas.genome_template import (
    GenomeTemplateCreate,
    GenomeTemplateEdgeCreate,
    GenomeTemplateGeneCreate,
    GenomeTemplateUpdate,
)


class GenomeTemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = GenomeTemplateRepository(db)

    async def create_template(self, user_id: int, payload: GenomeTemplateCreate):
        return await self.repo.create(
            user_id=user_id,
            name=payload.name,
            description=payload.description,
            species_group=payload.species_group,
            is_builtin=False,
        )

    async def list_templates(self, user_id: int):
        return await self.repo.list_by_user_id(user_id)

    async def get_template_details(self, template_id: int):
        return await self.repo.get_full_by_id(template_id)

    async def update_template(self, template_id: int, payload: GenomeTemplateUpdate):
        template = await self.repo.get_by_id(template_id)
        if template is None:
            return None, "template_not_found"

        if template.is_builtin:
            return None, "builtin_readonly"

        if payload.name is not None:
            template.name = payload.name
        if payload.description is not None:
            template.description = payload.description
        if payload.species_group is not None:
            template.species_group = payload.species_group
        if payload.base_predation_drive is not None:
            template.base_predation_drive = payload.base_predation_drive

        await self.db.commit()
        await self.db.refresh(template)
        return template, None

    async def delete_template(self, template_id: int):
        template = await self.repo.get_by_id(template_id)
        if template is None:
            return "template_not_found"

        if template.is_builtin:
            return "builtin_readonly"

        await self.repo.delete(template)
        return None

    async def add_gene(self, template_id: int, payload: GenomeTemplateGeneCreate):
        template = await self.repo.get_full_by_id(template_id)
        if template is None:
            return None, "template_not_found"

        if template.is_builtin:
            return None, "builtin_readonly"

        gene = GenomeTemplateGene(
            genome_template_id=template_id,
            name=payload.name,
            effect_type=payload.effect_type,
            chromosome_id=payload.chromosome_id,
            position=payload.position,
            default_active=payload.default_active,
            threshold=payload.threshold,
            x=payload.x,
            y=payload.y,
        )
        self.db.add(gene)

        gene_state = GenomeTemplateGeneState(
            genome_template_id=template_id,
            is_active=payload.default_active,
        )
        self.db.add(gene_state)

        await self.db.commit()
        await self.db.refresh(gene)
        return gene, None

    async def delete_gene(self, template_id: int, gene_id: int):
        template = await self.repo.get_full_by_id(template_id)
        if template is None:
            return "template_not_found"

        if template.is_builtin:
            return "builtin_readonly"

        gene = next((gene for gene in template.genes if gene.id == gene_id), None)
        if gene is None:
            return "gene_not_found"

        # сначала удаляем все рёбра, где участвует ген
        for edge in list(template.edges):
            if edge.source_gene_id == gene_id or edge.target_gene_id == gene_id:
                await self.db.delete(edge)

        # удаляем gene_state
        for state in list(template.gene_states):
            if state.gene_id == gene_id:
                await self.db.delete(state)

        await self.db.delete(gene)
        await self.db.commit()
        return None

    async def add_edge(self, template_id: int, payload: GenomeTemplateEdgeCreate):
        template = await self.repo.get_full_by_id(template_id)
        if template is None:
            return None, "template_not_found"

        if template.is_builtin:
            return None, "builtin_readonly"

        gene_ids = {gene.id for gene in template.genes}
        if payload.source_gene_id not in gene_ids:
            return None, "source_gene_not_found"
        if payload.target_gene_id not in gene_ids:
            return None, "target_gene_not_found"
        if payload.source_gene_id == payload.target_gene_id:
            return None, "same_gene"

        for edge in template.edges:
            if (
                edge.source_gene_id == payload.source_gene_id
                and edge.target_gene_id == payload.target_gene_id
            ):
                return None, "edge_exists"

        edge = GenomeTemplateEdge(
            genome_template_id=template_id,
            source_gene_id=payload.source_gene_id,
            target_gene_id=payload.target_gene_id,
            weight=payload.weight,
        )
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge, None

    async def delete_edge(self, template_id: int, edge_id: int):
        template = await self.repo.get_full_by_id(template_id)
        if template is None:
            return "template_not_found"

        if template.is_builtin:
            return "builtin_readonly"

        edge = next((edge for edge in template.edges if edge.id == edge_id), None)
        if edge is None:
            return "edge_not_found"

        await self.db.delete(edge)
        await self.db.commit()
        return None

    async def update_gene_position(
        self, template_id: int, gene_id: int, x: Optional[int], y: Optional[int]
    ):
        template = await self.repo.get_full_by_id(template_id)
        if template is None:
            return None, "template_not_found"

        if template.is_builtin:
            return None, "builtin_readonly"

        gene = next((gene for gene in template.genes if gene.id == gene_id), None)
        if gene is None:
            return None, "gene_not_found"

        gene.x = x
        gene.y = y

        await self.db.commit()
        await self.db.refresh(gene)
        return gene, None
