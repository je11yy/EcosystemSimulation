from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas import AvailableGenome, GenomeCreate, GenomeList, GenomeRead, Response
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
