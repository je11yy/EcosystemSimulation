from pydantic import BaseModel, Field

from ..agent import RuntimeAgent
from ..config import RuntimeSimConfig
from ..genome import RuntimeGene, RuntimeGeneEdge
from ..territory import RuntimeTerritory, RuntimeTerritoryEdge


class RuntimeGenome(BaseModel):
    id: int
    name: str = ""
    genes: list[RuntimeGene] = Field(default_factory=list)
    edges: list[RuntimeGeneEdge] = Field(default_factory=list)


class BuildSimulationRequest(BaseModel):
    simulation_id: int
    tick: int = 0
    config: RuntimeSimConfig = Field(default_factory=RuntimeSimConfig)
    territories: list[RuntimeTerritory] = Field(default_factory=list)
    territory_edges: list[RuntimeTerritoryEdge] = Field(default_factory=list)
    agents: list[RuntimeAgent] = Field(default_factory=list)
    genomes: list[RuntimeGenome] = Field(default_factory=list)
