import random
from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from simulation_core.agents.actions import ActionOption
from simulation_core.agents.genome import Genome, GenomeState
from simulation_core.agents.observation import Observation
from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.state import IndividualState
from simulation_core.config import SimConfig
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class ScoredOption:
    option: ActionOption
    utility: float


@runtime_checkable
class Policy(Protocol):
    def enumerate_options(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome: Genome,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> Sequence[ActionOption]: ...

    def score_options(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome: Genome,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        options: Sequence[ActionOption],
        cfg: SimConfig,
    ) -> Sequence[ScoredOption]: ...

    def choose(
        self,
        scored_options: Sequence[ScoredOption],
        rng: random.Random,
        cfg: SimConfig,
    ) -> ActionOption: ...

    def decide(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome: Genome,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        rng: random.Random,
        cfg: SimConfig,
    ) -> ActionOption: ...
