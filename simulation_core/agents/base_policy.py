import math
import random
from abc import ABC, abstractmethod
from typing import Sequence

from simulation_core.agents.actions import ActionOption
from simulation_core.agents.genome import Genome, GenomeState
from simulation_core.agents.observation import Observation
from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.policy import Policy, ScoredOption
from simulation_core.agents.state import IndividualState
from simulation_core.config import SimConfig
from simulation_core.world.api import WorldReadAPI


class BasePolicy(ABC, Policy):
    """
    Базовая реализация:
    decide = enumerate_options -> score_options -> choose
    """

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
    ) -> ActionOption:
        options = self.enumerate_options(
            state=state,
            phenotype=phenotype,
            genome=genome,
            genome_state=genome_state,
            obs=obs,
            world=world,
            cfg=cfg,
        )

        if not options:
            raise ValueError("Policy returned no available action options")

        scored = self.score_options(
            state=state,
            phenotype=phenotype,
            genome=genome,
            genome_state=genome_state,
            obs=obs,
            world=world,
            options=options,
            cfg=cfg,
        )

        if not scored:
            raise ValueError("Policy returned no scored options")

        return self.choose(
            scored_options=scored,
            rng=rng,
            cfg=cfg,
        )

    def choose(
        self,
        scored_options: Sequence[ScoredOption],
        rng: random.Random,
        cfg: SimConfig,
    ) -> ActionOption:
        beta = cfg.beta_default
        weights = [math.exp(beta * item.utility) for item in scored_options]
        chosen = rng.choices(scored_options, weights=weights, k=1)[0]
        return chosen.option

    @abstractmethod
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

    @abstractmethod
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
