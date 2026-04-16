from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.mappers.genome import genome_list_item_to_dict, genome_to_dict
from app.models import Genome
from app.models.relations.genome_user import GenomeUserRelation
from app.repositories.genome.genome import GenomeRepository
from app.schemas import GenomeCreate


class GenomeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.genomes = GenomeRepository(session)

    async def list_by_user(self, user_id: int) -> list[dict]:
        rows = await self.genomes.list_by_user(user_id)
        return [genome_list_item_to_dict(genome, owner_id) for genome, owner_id in rows]

    async def available_for_user(self, user_id: int) -> list[dict]:
        genomes = await self.genomes.available_for_user(user_id)
        return [{"id": genome.id, "name": genome.name} for genome in genomes]

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
