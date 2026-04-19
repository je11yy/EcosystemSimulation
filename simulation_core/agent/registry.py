from dataclasses import dataclass
from typing import Dict, List, Optional

from ..config import SimConfig
from ..genome.models import Genome
from .observation import Observation
from .state import AgentState


@dataclass
class Agent:
    state: AgentState
    genome: Genome
    pending_child_genome: Optional[Genome] = None
    pending_partner_id: Optional[int] = None

    def refresh_gene_effects(
        self,
        cfg: SimConfig,
        observation: Optional[Observation] = None,
    ) -> None:
        from ..genome.validation import validate_genome_for_agent_state

        self.genome = validate_genome_for_agent_state(
            self.genome,
            self.state,
            observation,
        )
        self.state.apply_gene_effects(self.genome, cfg)


class AgentRegistry:
    def __init__(self, cfg: Optional[SimConfig] = None):
        self.cfg = cfg or SimConfig()
        self.agents: Dict[int, Agent] = {}

    def add(
        self,
        state: AgentState,
        genome: Genome,
        observation: Optional[Observation] = None,
    ) -> None:
        from .factory import AgentFactory

        agent = AgentFactory(self.cfg).create(state, genome, observation)
        self.add_agent(agent)

    def add_agent(self, agent: Agent) -> None:
        self.agents[agent.state.id] = agent

    def get(self, agent_id: int) -> Agent:
        return self.agents[agent_id]

    def remove(self, agent_id: int) -> None:
        if agent_id in self.agents:
            del self.agents[agent_id]

    def all(self) -> List[Agent]:
        return list(self.agents.values())
