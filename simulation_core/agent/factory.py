from typing import Optional

from ..config import SimConfig
from ..genome.models import Genome
from .observation import Observation
from .registry import Agent
from .state import AgentState


class AgentFactory:
    def __init__(self, cfg: SimConfig):
        self.cfg = cfg

    def create(
        self,
        state: AgentState,
        genome: Genome,
        observation: Optional[Observation] = None,
    ) -> Agent:
        agent = Agent(state=state, genome=genome)
        agent.refresh_gene_effects(self.cfg, observation)
        return agent
