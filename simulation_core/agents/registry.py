from dataclasses import dataclass
from typing import Dict

from simulation_core.agents.genome import Genome, GenomeState
from simulation_core.agents.policy import Policy
from simulation_core.agents.state import IndividualState
from simulation_core.types import IndividualId


@dataclass
class Agent:
    """Представление агента в симуляции.

    Агент состоит из состояния, политики принятия решений,
    генома и текущего состояния генома.
    """

    state: IndividualState  # Физическое и репродуктивное состояние агента
    policy: Policy  # Политика принятия решений (мозг агента)
    genome: Genome  # Геном агента (наследственная информация)
    genome_state: GenomeState  # Текущее состояние генома (активные гены)


class AgentRegistry:
    """Реестр всех агентов в симуляции."""

    def __init__(self) -> None:
        self._agents: Dict[IndividualId, Agent] = {}  # Внутренний словарь агентов по ID

    def add(self, agent: Agent) -> None:
        self._agents[agent.state.id] = agent

    def get(self, agent_id: IndividualId) -> Agent:
        return self._agents[agent_id]

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    def remove(self, agent_id: IndividualId) -> None:
        self._agents.pop(agent_id, None)
