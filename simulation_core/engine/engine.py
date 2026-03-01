import random
from dataclasses import dataclass
from typing import List

from simulation_core.agents.actions import ActionOption
from simulation_core.agents.observation import Observation
from simulation_core.agents.registry import Agent, AgentRegistry
from simulation_core.config import SimConfig
from simulation_core.types import Tick
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class Decision:
    tick: Tick
    agent_id: str
    chosen: ActionOption


class SimulationEngine:
    def __init__(self, cfg: SimConfig, world: WorldReadAPI, seed: int = 0) -> None:
        self.cfg = cfg
        self.world = world
        self.rng = random.Random(seed)
        self.tick: Tick = Tick(0)
        self.agents = AgentRegistry()

    def add_agent(self, agent: Agent) -> None:
        agent.state.validate(self.cfg)
        self.agents.add(agent)

    def build_observation(self, agent: Agent) -> Observation:
        current_id = agent.state.location

        individuals_here = [
            a.state.id
            for a in self.agents.all()
            if a.state.location == current_id and a.state.id != agent.state.id
        ]

        neighbor_territories = [edge.to for edge in self.world.graph().neighbors(current_id)]

        return Observation(
            current_id=current_id,
            individuals_here=individuals_here,
            neighbor_territories=neighbor_territories,
        )

    def step_decisions_only(self) -> List[Decision]:
        decisions: List[Decision] = []

        for agent in self.agents.all():
            obs = self.build_observation(agent)
            chosen = agent.policy.decide(
                state=agent.state,
                obs=obs,
                world=self.world,
                rng=self.rng,
                cfg=self.cfg,
            )
            decisions.append(Decision(tick=self.tick, agent_id=str(agent.state.id), chosen=chosen))

        self.tick = Tick(int(self.tick) + 1)
        return decisions
