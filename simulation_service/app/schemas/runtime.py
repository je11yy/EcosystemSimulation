from typing import Any, Optional

from pydantic import BaseModel


class RuntimeTerritoryDTO(BaseModel):
    id: str
    food: float
    temperature: float
    food_regen_per_tick: float
    food_capacity: float
    x: Optional[int] = None
    y: Optional[int] = None


class RuntimeTerritoryEdgeDTO(BaseModel):
    source_id: str
    target_id: str
    movement_cost: float


class RuntimeGeneDTO(BaseModel):
    id: str
    name: str
    chromosome_id: str
    position: float
    default_active: bool
    threshold: float


class RuntimeGeneEdgeDTO(BaseModel):
    source_gene_id: str
    target_gene_id: str
    weight: float


class RuntimeGeneStateDTO(BaseModel):
    gene_id: str
    is_active: bool


class RuntimeAgentDTO(BaseModel):
    id: str
    location: str

    hunger: int
    hp: int

    base_strength: int
    base_defense: int

    sex: str
    pregnant: bool
    ticks_to_birth: int
    father_id: Optional[str] = None

    base_temp_pref: float
    satisfaction: float
    alive: bool

    genes: list[RuntimeGeneDTO]
    gene_edges: list[RuntimeGeneEdgeDTO]
    gene_states: list[RuntimeGeneStateDTO]


class RuntimeConfigDTO(BaseModel):
    hunger_min: int = 0
    hunger_max: int = 5

    strength_min: int = 1
    strength_max: int = 5

    defense_min: int = 1
    defense_max: int = 5

    hp_min: int = 0
    hp_max: int = 5

    pregnancy_duration_ticks: int = 3
    beta_default: float = 2.0


class SimulationInitDTO(BaseModel):
    simulation_id: str
    tick: int
    config: RuntimeConfigDTO
    territories: list[RuntimeTerritoryDTO]
    territory_edges: list[RuntimeTerritoryEdgeDTO]
    agents: list[RuntimeAgentDTO]


class RuntimeStartResponseDTO(BaseModel):
    ok: bool
    simulation_id: str
    tick: int
    loaded_agents: int
    loaded_territories: int


class RuntimeStateResponseDTO(BaseModel):
    ok: bool
    simulation_id: str
    state: dict[Any, Any]


class RuntimeDeleteResponseDTO(BaseModel):
    ok: bool
    simulation_id: str
    removed: bool
