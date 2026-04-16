from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Gene, GeneEdge, Genome
from app.models.relations.genome_gene import GenomeGeneRelation
from app.models.relations.genome_user import GenomeUserRelation
from app.repositories.base import Repository


class GenomeRepository(Repository):
    async def list_by_user(self, user_id: int) -> list[tuple[Genome, int]]:
        stmt = (
            select(Genome, GenomeUserRelation.user_id)
            .join(GenomeUserRelation, GenomeUserRelation.genome_id == Genome.id)
            .where(GenomeUserRelation.user_id == user_id)
            .order_by(Genome.updated_at.desc(), Genome.id.desc())
            .options(selectinload(Genome.user_links))
        )
        return list((await self.session.execute(stmt)).all())

    async def available_for_user(self, user_id: int) -> list[Genome]:
        stmt = (
            select(Genome)
            .outerjoin(GenomeUserRelation, GenomeUserRelation.genome_id == Genome.id)
            .where((Genome.is_template.is_(True)) | (GenomeUserRelation.user_id == user_id))
            .order_by(Genome.name)
        )
        return list((await self.session.scalars(stmt)).unique().all())

    async def get_with_graph(self, genome_id: int) -> Genome | None:
        stmt = (
            select(Genome)
            .where(Genome.id == genome_id)
            .options(
                selectinload(Genome.user_links),
                selectinload(Genome.gene_links).selectinload(GenomeGeneRelation.gene),
            )
        )
        genome = await self.session.scalar(stmt)
        if genome is None:
            return None

        genes = [link.gene for link in genome.gene_links]
        gene_ids = {gene.id for gene in genes}
        if gene_ids:
            (
                await self.session.scalars(
                    select(GeneEdge)
                    .where(GeneEdge.source_id.in_(gene_ids), GeneEdge.target_id.in_(gene_ids))
                    .options(
                        selectinload(GeneEdge.source_gene),
                        selectinload(GeneEdge.target_gene),
                    )
                )
            ).all()
            (
                await self.session.scalars(
                    select(Gene)
                    .where(Gene.id.in_(gene_ids))
                    .options(selectinload(Gene.outgoing_edges))
                )
            ).all()

        return genome

    async def get_available_with_graph(self, genome_id: int, user_id: int) -> Genome | None:
        stmt = (
            select(Genome)
            .outerjoin(GenomeUserRelation, GenomeUserRelation.genome_id == Genome.id)
            .where(
                Genome.id == genome_id,
                (Genome.is_template.is_(True)) | (GenomeUserRelation.user_id == user_id),
            )
            .options(
                selectinload(Genome.user_links),
                selectinload(Genome.gene_links).selectinload(GenomeGeneRelation.gene),
            )
        )
        genome = await self.session.scalar(stmt)
        if genome is None:
            return None

        genes = [link.gene for link in genome.gene_links]
        gene_ids = {gene.id for gene in genes}
        if gene_ids:
            (
                await self.session.scalars(
                    select(GeneEdge)
                    .where(GeneEdge.source_id.in_(gene_ids), GeneEdge.target_id.in_(gene_ids))
                    .options(
                        selectinload(GeneEdge.source_gene),
                        selectinload(GeneEdge.target_gene),
                    )
                )
            ).all()
            (
                await self.session.scalars(
                    select(Gene)
                    .where(Gene.id.in_(gene_ids))
                    .options(selectinload(Gene.outgoing_edges))
                )
            ).all()

        return genome
