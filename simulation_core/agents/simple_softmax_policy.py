from dataclasses import dataclass
from typing import Sequence

from simulation_core.agents.actions import ActionOption, ActionType
from simulation_core.agents.base_policy import BasePolicy
from simulation_core.agents.genome import Genome, GenomeState
from simulation_core.agents.observation import Observation
from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.policy import ScoredOption
from simulation_core.agents.state import IndividualState
from simulation_core.config import SimConfig
from simulation_core.types import TerritoryId
from simulation_core.world.api import WorldReadAPI


@dataclass
class SimpleSoftmaxPolicy(BasePolicy):
    def enumerate_options(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome: Genome,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> Sequence[ActionOption]:
        options: list[ActionOption] = []

        current_territory = world.get_territory(obs.current_id)

        options.append(ActionOption(type=ActionType.REST))

        if current_territory.food >= 1:
            options.append(ActionOption(type=ActionType.EAT))

        for territory_id in obs.neighbor_territories:
            options.append(
                ActionOption(
                    type=ActionType.MOVE,
                    to_territory=territory_id,
                )
            )

        if not state.pregnant:
            for partner_id in obs.individuals_here:
                options.append(
                    ActionOption(
                        type=ActionType.MATE,
                        partner_id=partner_id,
                    )
                )

        return options

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
    ) -> Sequence[ScoredOption]:
        scored: list[ScoredOption] = []

        for option in options:
            utility = self._score_single_option(
                option=option,
                state=state,
                phenotype=phenotype,
                genome=genome,
                genome_state=genome_state,
                obs=obs,
                world=world,
                cfg=cfg,
            )
            scored.append(ScoredOption(option=option, utility=utility))

        return scored

    def _score_single_option(
        self,
        option: ActionOption,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome: Genome,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        if option.type == ActionType.EAT:
            return self._score_eat(
                state=state,
                phenotype=phenotype,
                genome_state=genome_state,
                obs=obs,
                world=world,
                cfg=cfg,
            )

        if option.type == ActionType.MOVE:
            if option.to_territory is None:
                raise ValueError("MOVE action requires to_territory")
            return self._score_move(
                target_territory_id=option.to_territory,
                state=state,
                phenotype=phenotype,
                genome_state=genome_state,
                world=world,
                cfg=cfg,
            )

        if option.type == ActionType.REST:
            return self._score_rest(
                state=state,
                phenotype=phenotype,
                genome_state=genome_state,
                obs=obs,
                world=world,
                cfg=cfg,
            )

        if option.type == ActionType.MATE:
            if option.partner_id is None:
                raise ValueError("MATE action requires partner_id")
            return self._score_mate(
                state=state,
                phenotype=phenotype,
                genome_state=genome_state,
                cfg=cfg,
            )

        raise ValueError(f"Unsupported action type: {option.type}")

    def _score_eat(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        territory = world.get_territory(obs.current_id)

        hunger_need = state.hunger / cfg.hunger_max
        food_bonus = 0.2 if territory.food >= 1 else -1000.0

        utility = 2.0 * hunger_need + food_bonus

        if genome_state.is_active("g_hunger_drive"):
            utility += 0.7

        return utility

    def _score_move(
        self,
        target_territory_id: TerritoryId,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome_state: GenomeState,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        territory = world.get_territory(target_territory_id)

        food_score = min(territory.food / 5.0, 1.0)

        temperature_gap = abs(territory.temperature - phenotype.temp_pref)
        temperature_score = max(0.0, 1.0 - temperature_gap / 20.0)

        utility = 1.2 * food_score + 1.0 * temperature_score
        utility -= (state.hunger / cfg.hunger_max) * 0.5

        if genome_state.is_active("g_risk_move"):
            utility += 0.4

        if (
            genome_state.is_active("g_heat_resistance")
            and territory.temperature > phenotype.temp_pref
        ):
            utility += 0.3

        if (
            genome_state.is_active("g_cold_resistance")
            and territory.temperature < phenotype.temp_pref
        ):
            utility += 0.3

        return utility

    def _score_rest(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome_state: GenomeState,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        current_territory = world.get_territory(obs.current_id)

        temperature_gap = abs(current_territory.temperature - phenotype.temp_pref)
        comfort_score = max(0.0, 1.0 - temperature_gap / 20.0)
        hunger_penalty = state.hunger / cfg.hunger_max

        utility = 0.3 * comfort_score - 0.8 * hunger_penalty

        if genome_state.is_active("g_low_activity"):
            utility += 0.4

        return utility

    def _score_mate(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        genome_state: GenomeState,
        cfg: SimConfig,
    ) -> float:
        if state.pregnant:
            return -1000.0

        hunger_penalty = state.hunger / cfg.hunger_max
        utility = 1.0 - 1.2 * hunger_penalty

        if genome_state.is_active("g_reproduction_drive"):
            utility += 0.5

        return utility
