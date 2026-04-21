import random
from dataclasses import dataclass

from ..agent.observation import Observation
from ..agent.registry import Agent, AgentRegistry
from ..world import WorldState
from .costs import ActionCostCalculator


@dataclass(frozen=True)
class DecisionContext:
    agent: Agent
    agents: AgentRegistry
    world: WorldState
    observation: Observation
    cost_calculator: ActionCostCalculator

    @property
    def current_location(self):
        return self.world.get_territory(self.agent.state.location)


@dataclass(frozen=True)
class StepContext:
    tick: int
    world: WorldState
    agents: AgentRegistry
    cost_calculator: ActionCostCalculator
    rng: random.Random
