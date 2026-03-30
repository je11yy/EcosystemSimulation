from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.genome_template import (
    GenomeTemplateCreate,
    GenomeTemplateDetailsRead,
    GenomeTemplateEdgeCreate,
    GenomeTemplateEdgeRead,
    GenomeTemplateGeneCreate,
    GenomeTemplateGenePositionUpdate,
    GenomeTemplateGeneRead,
    GenomeTemplateRead,
    GenomeTemplateUpdate,
)
from app.services.builtin_genome_template_seeder import BuiltinGenomeTemplateSeeder
from app.services.genome_template_service import GenomeTemplateService

router = APIRouter(prefix="/genome-templates", tags=["genome-templates"])


async def _ensure_user_exists(db: AsyncSession, user_id: int) -> None:
    existing = await db.execute(select(User).where(User.id == user_id))
    if existing.scalar_one_or_none() is None:
        db.add(
            User(
                id=user_id,
                email=f"user{user_id}@example.com",
                hashed_password="placeholder",
            )
        )
        await db.flush()


@router.get("", response_model=list[GenomeTemplateRead])
async def list_genome_templates(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _ensure_user_exists(db, user_id)
    seeder = BuiltinGenomeTemplateSeeder()
    await seeder.seed_for_user(db, user_id)

    service = GenomeTemplateService(db)
    return await service.list_templates(user_id)


@router.post("", response_model=GenomeTemplateRead)
async def create_genome_template(
    payload: GenomeTemplateCreate,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _ensure_user_exists(db, user_id)
    service = GenomeTemplateService(db)
    return await service.create_template(user_id, payload)


@router.get("/{template_id}", response_model=GenomeTemplateDetailsRead)
async def get_genome_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = GenomeTemplateService(db)
    template = await service.get_template_details(template_id)

    if template is None:
        raise HTTPException(status_code=404, detail="Genome template not found")

    return {
        "template": template,
        "genes": template.genes,
        "edges": template.edges,
        "gene_states": template.gene_states,
    }


@router.patch("/{template_id}", response_model=GenomeTemplateRead)
async def update_genome_template(
    template_id: int,
    payload: GenomeTemplateUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = GenomeTemplateService(db)
    template, error = await service.update_template(template_id, payload)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return template


@router.delete("/{template_id}")
async def delete_genome_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = GenomeTemplateService(db)
    error = await service.delete_template(template_id)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return {"ok": True, "template_id": template_id}


@router.post("/{template_id}/genes", response_model=GenomeTemplateGeneRead)
async def add_gene_to_template(
    template_id: int,
    payload: GenomeTemplateGeneCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = GenomeTemplateService(db)
    gene, error = await service.add_gene(template_id, payload)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return gene


@router.delete("/{template_id}/genes/{gene_id}")
async def delete_gene_from_template(
    template_id: int,
    gene_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = GenomeTemplateService(db)
    error = await service.delete_gene(template_id, gene_id)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "gene_not_found":
        raise HTTPException(status_code=404, detail="Gene not found")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return {"ok": True, "gene_id": gene_id}


@router.post("/{template_id}/edges", response_model=GenomeTemplateEdgeRead)
async def add_edge_to_template(
    template_id: int,
    payload: GenomeTemplateEdgeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    print(f"DEBUG payload: {payload}")
    print(f"DEBUG source_gene_id type: {type(payload.source_gene_id)}")
    service = GenomeTemplateService(db)
    edge, error = await service.add_edge(template_id, payload)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "source_gene_not_found":
        raise HTTPException(status_code=404, detail="Source gene not found")
    if error == "target_gene_not_found":
        raise HTTPException(status_code=404, detail="Target gene not found")
    if error == "same_gene":
        raise HTTPException(status_code=400, detail="Cannot connect gene to itself")
    if error == "edge_exists":
        raise HTTPException(status_code=400, detail="Edge already exists")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return edge


@router.delete("/{template_id}/edges/{edge_id}")
async def delete_edge_from_template(
    template_id: int,
    edge_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    service = GenomeTemplateService(db)
    error = await service.delete_edge(template_id, edge_id)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "edge_not_found":
        raise HTTPException(status_code=404, detail="Edge not found")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return {"ok": True, "edge_id": edge_id}


@router.patch("/{template_id}/genes/{gene_id}/position", response_model=GenomeTemplateGeneRead)
async def update_gene_position(
    template_id: int,
    gene_id: int,
    payload: GenomeTemplateGenePositionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = GenomeTemplateService(db)
    gene, error = await service.update_gene_position(template_id, gene_id, payload.x, payload.y)

    if error == "template_not_found":
        raise HTTPException(status_code=404, detail="Genome template not found")
    if error == "gene_not_found":
        raise HTTPException(status_code=404, detail="Gene not found")
    if error == "builtin_readonly":
        raise HTTPException(status_code=400, detail="Built-in template is read-only")

    return gene
