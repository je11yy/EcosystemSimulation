from __future__ import annotations

import random
from typing import Protocol, Sequence, runtime_checkable

from simulation_core.agents.actions import ActionOption
from simulation_core.agents.observation import Observation
from simulation_core.agents.state import IndividualState
from simulation_core.config import SimConfig
from simulation_core.world.api import WorldReadAPI


@runtime_checkable
class Policy(Protocol):
    def enumerate_options(
        self,
        state: IndividualState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> Sequence[ActionOption]: ...

    def score_options(
        self,
        state: IndividualState,
        obs: Observation,
        world: WorldReadAPI,
        options: Sequence[ActionOption],
        cfg: SimConfig,
    ): ...

    def choose(
        self,
        scored_options,
        rng: random.Random,
        cfg: SimConfig,
    ) -> ActionOption: ...

    def decide(
        self,
        state: IndividualState,
        obs: Observation,
        world: WorldReadAPI,
        rng: random.Random,
        cfg: SimConfig,
    ) -> ActionOption: ...
