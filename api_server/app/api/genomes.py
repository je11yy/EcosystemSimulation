from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import (
    AvailableGenome,
    GeneCreate,
    GeneEdgeCreate,
    GenomeCreate,
    GenomeList,
    GenomeRead,
    Position,
    Response,
)
from app.services.genome.service import GenomeService

router = APIRouter(prefix="/genomes", tags=["genomes"])


@router.get("", response_model=list[GenomeList])
async def get_genomes(current_user: CurrentUser, db: DbSession) -> list[dict]:
    return await GenomeService(db).list_by_user(current_user.id)


@router.get("/available", response_model=list[AvailableGenome])
async def get_available_genomes(current_user: CurrentUser, db: DbSession) -> list[dict]:
    return await GenomeService(db).available_for_user(current_user.id)


@router.post("", response_model=Response)
async def create_genome(
    genome: GenomeCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await GenomeService(db).create(current_user.id, genome)
    return Response(success=True, message="Genome created")


@router.get("/{genome_id}", response_model=GenomeRead)
async def get_genome(genome_id: int, current_user: CurrentUser, db: DbSession) -> dict:
    return await GenomeService(db).get(genome_id, current_user.id)


@router.post("/{genome_id}/genes", response_model=Response)
async def create_gene(
    genome_id: int,
    gene: GeneCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await GenomeService(db).create_gene(genome_id, current_user.id, gene)
    return Response(success=True, message="Gene created")


@router.post("/{genome_id}/edges", response_model=Response)
async def create_edge(
    genome_id: int,
    edge: GeneEdgeCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await GenomeService(db).create_edge(genome_id, current_user.id, edge)
    return Response(success=True, message="Gene edge created")


@router.put("/{genome_id}/genes/{gene_id}", response_model=Response)
async def update_gene(
    genome_id: int,
    gene_id: int,
    gene: GeneCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await GenomeService(db).update_gene(genome_id, gene_id, current_user.id, gene)
    return Response(success=True, message="Gene updated")


@router.delete("/{genome_id}/genes/{gene_id}", response_model=Response)
async def delete_gene(
    genome_id: int,
    gene_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await GenomeService(db).delete_gene(genome_id, gene_id, current_user.id)
    return Response(success=True, message="Gene deleted")


@router.put("/{genome_id}/genes/{gene_id}/position", response_model=Response)
async def update_gene_position(
    genome_id: int,
    gene_id: int,
    position: Position,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    await GenomeService(db).update_gene_position(genome_id, gene_id, current_user.id, position)
    return Response(success=True, message="Gene position updated")
