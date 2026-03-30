from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from simulation_core.agents.genome.effect_type import GeneEffectType


class GenomeTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    species_group: str = Field(min_length=1, max_length=128)
    base_predation_drive: float = 0.0


class GenomeTemplateUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    species_group: Optional[str] = Field(default=None, min_length=1, max_length=128)
    base_predation_drive: Optional[float] = None


class GenomeTemplateRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    is_builtin: bool
    species_group: str
    base_predation_drive: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenomeTemplateGeneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    chromosome_id: str = Field(min_length=1, max_length=64)
    effect_type: GeneEffectType
    position: float
    default_active: bool = False
    threshold: float = 0.0
    x: Optional[int] = None
    y: Optional[int] = None


class GenomeTemplateGeneRead(BaseModel):
    id: int
    genome_template_id: int
    name: str
    chromosome_id: str
    position: float
    default_active: bool
    threshold: float
    x: Optional[int] = None
    y: Optional[int] = None
    effect_type: GeneEffectType

    model_config = {"from_attributes": True}


class GenomeTemplateEdgeCreate(BaseModel):
    source_gene_id: int
    target_gene_id: int
    weight: float


class GenomeTemplateEdgeRead(BaseModel):
    id: int
    genome_template_id: int
    source_gene_id: int
    target_gene_id: int
    weight: float

    model_config = {"from_attributes": True}


class GenomeTemplateGeneStateCreate(BaseModel):
    genome_template_id: int
    is_active: bool


class GenomeTemplateGeneStateRead(BaseModel):
    id: int
    genome_template_id: int
    is_active: bool

    model_config = {"from_attributes": True}


class GenomeTemplateDetailsRead(BaseModel):
    template: GenomeTemplateRead
    genes: list[GenomeTemplateGeneRead]
    edges: list[GenomeTemplateEdgeRead]
    gene_states: list[GenomeTemplateGeneStateRead]


class GenomeTemplateGenePositionUpdate(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
