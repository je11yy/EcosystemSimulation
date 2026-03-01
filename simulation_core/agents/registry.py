from dataclasses import dataclass
from typing import Dict

from simulation_core.agents.policy import Policy
from simulation_core.agents.state import IndividualState
from simulation_core.types import IndividualId


@dataclass
class Agent:
    state: IndividualState
    policy: Policy


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: Dict[IndividualId, Agent] = {}

    def add(self, agent: Agent) -> None:
        self._agents[agent.state.id] = agent

    def get(self, agent_id: IndividualId) -> Agent:
        return self._agents[agent_id]

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    def remove(self, agent_id: IndividualId) -> None:
        self._agents.pop(agent_id, None)
