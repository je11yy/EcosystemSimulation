"""
Pydantic schemas for API request/response validation
"""

from .agent.create import AgentCreate
from .agent.read import AgentRead, AgentResponse
from .auth import AuthCredentials, UserRead
from .base import Node, Position, Response
from .genome import AvailableGenome, GenomeCreate, GenomeList, GenomeRead
from .genome.edge import GeneEdge
from .genome.gene import Gene
from .simulation.create import SimulationCreate
from .simulation.log import (
    AgentDecision,
    SimulationLogCreate,
    SimulationLogRead,
    StepResult,
    TickMetrics,
)
from .simulation.read import SimulationDetails, SimulationLogListItem, SimulationRead
from .territory.edge import TerritoryEdge
from .territory.territory import (
    TerritoryCreate,
    TerritoryEdgeCreate,
    TerritoryEdgeRead,
    TerritoryRead,
)

Step = StepResult
Log = SimulationLogRead

__all__ = [
    # Base
    "Response",
    "Position",
    "Node",
    # Auth
    "AuthCredentials",
    "UserRead",
    # Step
    "Step",
    "Log",
    # Agent
    "AgentCreate",
    "AgentRead",
    "AgentResponse",
    # Simulation
    "SimulationRead",
    "SimulationCreate",
    "SimulationDetails",
    "AgentDecision",
    "SimulationLogCreate",
    "SimulationLogListItem",
    "SimulationLogRead",
    "StepResult",
    "TickMetrics",
    # Territory
    "TerritoryCreate",
    "TerritoryRead",
    "TerritoryEdgeCreate",
    "TerritoryEdgeRead",
    "TerritoryEdge",
    # Genome
    "Gene",
    "GeneEdge",
    "AvailableGenome",
    "GenomeRead",
    "GenomeList",
    "GenomeCreate",
]
