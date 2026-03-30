from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.genome_template import GenomeTemplate


class GenomeTemplateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        user_id: int,
        name: str,
        species_group: str,
        description: Optional[str] = None,
        is_builtin: bool = False,
    ) -> GenomeTemplate:
        template = GenomeTemplate(
            user_id=user_id,
            name=name,
            description=description,
            species_group=species_group,
            is_builtin=is_builtin,
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_by_id(self, template_id: int) -> Optional[GenomeTemplate]:
        stmt = select(GenomeTemplate).where(GenomeTemplate.id == template_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_full_by_id(self, template_id: int) -> Optional[GenomeTemplate]:
        stmt = (
            select(GenomeTemplate)
            .where(GenomeTemplate.id == template_id)
            .options(
                selectinload(GenomeTemplate.genes),
                selectinload(GenomeTemplate.edges),
                selectinload(GenomeTemplate.gene_states),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: int) -> list[GenomeTemplate]:
        stmt = (
            select(GenomeTemplate)
            .where(GenomeTemplate.user_id == user_id)
            .order_by(GenomeTemplate.is_builtin.desc(), GenomeTemplate.id.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, template: GenomeTemplate) -> None:
        await self.db.delete(template)
        await self.db.commit()
