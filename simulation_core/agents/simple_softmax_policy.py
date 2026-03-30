from dataclasses import dataclass, field
from typing import Sequence

from simulation_core.agents.actions import ActionOption, ActionType
from simulation_core.agents.base_policy import BasePolicy
from simulation_core.agents.genome import Genome, GenomeState
from simulation_core.agents.observation import (
    Observation,
    ObservedIndividual,
)
from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.policy import ScoredOption
from simulation_core.agents.state import IndividualState
from simulation_core.agents.traits import TraitAggregator, TraitVector
from simulation_core.config import SimConfig
from simulation_core.types import IndividualId, TerritoryId
from simulation_core.world.api import WorldReadAPI


@dataclass
class SimpleSoftmaxPolicy(BasePolicy):
    trait_aggregator: TraitAggregator = field(default_factory=TraitAggregator)

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
        del phenotype, genome, genome_state, cfg

        options: list[ActionOption] = []

        current_territory = world.get_territory(obs.current_id)

        options.append(ActionOption(type=ActionType.REST))

        if current_territory.food >= 1:
            options.append(ActionOption(type=ActionType.EAT))

        for territory in obs.neighbor_territories:
            options.append(
                ActionOption(
                    type=ActionType.MOVE,
                    to_territory=territory.id,
                )
            )

        if not state.pregnant:
            for partner in obs.individuals_here:
                if not partner.alive:
                    continue
                if partner.sex == state.sex:
                    continue
                if partner.species_group != state.species_group:
                    continue

                options.append(
                    ActionOption(
                        type=ActionType.MATE,
                        partner_id=partner.id,
                    )
                )

        if self._hunt_enumeration_enabled():
            for target in obs.individuals_here:
                if self._is_hunt_candidate(
                    actor_state=state,
                    target=target,
                ):
                    options.append(
                        ActionOption(
                            type=ActionType.HUNT,
                            target_id=target.id,
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

        traits = self.trait_aggregator.aggregate(
            state=state,
            phenotype=phenotype,
            genome=genome,
            genome_state=genome_state,
            obs=obs,
            world=world,
            cfg=cfg,
        )

        for option in options:
            utility = self._score_single_option(
                option=option,
                state=state,
                phenotype=phenotype,
                traits=traits,
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
        traits: TraitVector,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        if option.type == ActionType.EAT:
            return self._score_eat(
                state=state,
                phenotype=phenotype,
                traits=traits,
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
                traits=traits,
                obs=obs,
                world=world,
                cfg=cfg,
            )

        if option.type == ActionType.REST:
            return self._score_rest(
                state=state,
                phenotype=phenotype,
                traits=traits,
                obs=obs,
                world=world,
                cfg=cfg,
            )

        if option.type == ActionType.MATE:
            if option.partner_id is None:
                raise ValueError("MATE action requires partner_id")
            return self._score_mate(
                partner_id=option.partner_id,
                state=state,
                phenotype=phenotype,
                traits=traits,
                obs=obs,
                world=world,
                cfg=cfg,
            )

        if option.type == ActionType.HUNT:
            if option.target_id is None:
                raise ValueError("HUNT action requires target_id")
            return self._score_hunt(
                target_id=option.target_id,
                state=state,
                phenotype=phenotype,
                traits=traits,
                obs=obs,
                world=world,
                cfg=cfg,
            )

        raise ValueError(f"Unsupported action type: {option.type}")

    def _score_eat(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        traits: TraitVector,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        del phenotype

        territory = world.get_territory(obs.current_id)
        hunger_need = state.hunger / cfg.hunger_max if cfg.hunger_max > 0 else 0.0
        local_food_ratio = self._food_ratio(territory.food, territory.food_capacity)
        local_density_ratio = self._density_ratio(len(obs.individuals_here) + 1)

        utility = 1.8 * hunger_need
        utility += 0.9 * traits.feeding_drive
        utility += 0.6 * traits.food_opportunism * local_food_ratio
        utility += 0.2 * territory.food

        utility -= 0.45 * local_density_ratio
        utility += 0.30 * traits.social_tolerance * local_density_ratio

        if state.hunger >= cfg.hunger_max - 1:
            utility += 1.5

        if territory.food < 1:
            return -1000.0

        return utility

    def _score_move(
        self,
        target_territory_id: TerritoryId,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        traits: TraitVector,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        del cfg

        current = world.get_territory(obs.current_id)
        observed_target = obs.get_neighbor_territory(target_territory_id)
        if observed_target is None:
            return -1000.0

        current_patch_value = self._estimate_patch_value(
            food=current.food,
            food_capacity=current.food_capacity,
            temperature=current.temperature,
            movement_cost=0.0,
            occupant_count=len(obs.individuals_here) + 1,
            state=state,
            phenotype=phenotype,
            traits=traits,
        )
        target_patch_value = self._estimate_patch_value(
            food=observed_target.food,
            food_capacity=observed_target.food_capacity,
            temperature=observed_target.temperature,
            movement_cost=observed_target.movement_cost,
            occupant_count=observed_target.occupant_count,
            state=state,
            phenotype=phenotype,
            traits=traits,
        )

        patch_gain = target_patch_value - current_patch_value

        utility = 0.0
        utility += patch_gain
        utility += 0.65 * traits.movement_drive
        utility += 0.25 * traits.risk_taking
        utility -= 0.85 * traits.site_fidelity

        return utility

    def _score_rest(
        self,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        traits: TraitVector,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        current = world.get_territory(obs.current_id)
        temperature_gap = abs(current.temperature - phenotype.temp_pref)
        comfort_score = max(0.0, 1.0 - temperature_gap / 20.0)
        hunger_penalty = state.hunger / cfg.hunger_max if cfg.hunger_max > 0 else 0.0
        local_density_ratio = self._density_ratio(len(obs.individuals_here) + 1)

        utility = 0.2
        utility += 0.8 * max(0.0, -traits.activity_level)
        utility += 0.5 * comfort_score
        utility += 0.35 * traits.site_fidelity
        utility += 0.2 * traits.defense_drive
        utility += 0.2 * traits.escape_drive

        utility -= 0.35 * local_density_ratio
        utility += 0.25 * traits.social_tolerance * local_density_ratio

        utility -= 1.0 * hunger_penalty
        utility -= 0.5 * traits.feeding_drive
        utility -= 0.4 * traits.reproduction_drive

        return utility

    def _score_mate(
        self,
        partner_id: IndividualId,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        traits: TraitVector,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        partner = obs.get_individual(partner_id)
        if partner is None:
            return -1000.0

        if not partner.alive:
            return -1000.0

        if state.pregnant:
            return -1000.0

        current = world.get_territory(obs.current_id)
        hunger_penalty = state.hunger / cfg.hunger_max if cfg.hunger_max > 0 else 0.0
        temperature_gap = abs(current.temperature - phenotype.temp_pref)
        comfort_score = max(0.0, 1.0 - temperature_gap / 20.0)
        local_density = self._density_ratio(len(obs.individuals_here) + 1)

        utility = 0.1
        utility += 1.0 * traits.reproduction_drive
        utility += 0.15 * local_density
        utility += 0.2 * comfort_score

        utility += 0.20 * traits.social_tolerance * local_density
        utility -= 0.15 * max(0.0, local_density - 0.5)

        utility -= 1.2 * hunger_penalty
        utility -= 0.6 * traits.mate_selectivity * hunger_penalty
        utility -= 0.35 * traits.parental_investment * hunger_penalty
        utility -= 0.25 * traits.parental_investment * (1.0 - comfort_score)

        utility -= 0.25 * traits.feeding_drive
        utility -= 0.2 * traits.predation_drive

        return utility

    def _score_hunt(
        self,
        target_id: IndividualId,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        traits: TraitVector,
        obs: Observation,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> float:
        target = obs.get_individual(target_id)
        if target is None:
            return -1000.0

        if not self._is_hunt_candidate(actor_state=state, target=target):
            return -1000.0

        if state.hunt_cooldown > 0:
            return -1000.0

        current = world.get_territory(obs.current_id)

        hunger_ratio = state.hunger / cfg.hunger_max if cfg.hunger_max > 0 else 0.0
        food_scarcity = 1.0 - self._food_ratio(current.food, current.food_capacity)
        local_density_ratio = self._density_ratio(len(obs.individuals_here) + 1)

        strength_advantage = (phenotype.strength - target.effective_defense) / 5.0
        retaliation_risk = max(0.0, (target.effective_strength - phenotype.defense) / 5.0)

        same_species_penalty = 0.0
        if target.species_group == state.species_group:
            same_species_penalty = 1.2 * max(0.0, 1.0 - traits.cannibal_tolerance)

        utility = 0.0
        utility += 1.2 * traits.predation_drive
        utility += 0.8 * hunger_ratio
        utility += 0.7 * food_scarcity
        utility += 0.3 * local_density_ratio
        utility += 0.8 * strength_advantage
        utility -= 0.9 * retaliation_risk
        utility += 0.3 * traits.aggression_drive
        utility -= 0.4 * traits.escape_drive
        utility -= same_species_penalty

        return utility

    def _estimate_patch_value(
        self,
        food: float,
        food_capacity: float,
        temperature: float,
        movement_cost: float,
        occupant_count: int,
        state: IndividualState,
        phenotype: PhenotypeSnapshot,
        traits: TraitVector,
    ) -> float:
        hunger_ratio = self._safe_ratio(state.hunger, 5.0)
        food_ratio = self._food_ratio(food, food_capacity)
        temperature_gap = abs(temperature - phenotype.temp_pref)
        thermal_comfort = max(0.0, 1.0 - temperature_gap / 20.0)
        density_ratio = self._density_ratio(occupant_count)

        crowding_penalty = 0.7 * density_ratio
        crowding_penalty -= 0.45 * traits.social_tolerance * density_ratio
        crowding_penalty += 0.25 * traits.kin_avoidance * density_ratio

        value = 0.0
        value += (0.9 + 0.8 * traits.feeding_drive) * food_ratio
        value += (0.5 + 0.5 * traits.habitat_sensitivity) * thermal_comfort
        value += 0.2 * traits.site_fidelity * thermal_comfort
        value -= crowding_penalty
        value -= 0.35 * movement_cost
        value -= 0.2 * hunger_ratio * movement_cost

        if temperature > phenotype.temp_pref:
            value += 0.2 * traits.heat_resistance

        if temperature < phenotype.temp_pref:
            value += 0.2 * traits.cold_resistance

        return value

    def _is_hunt_candidate(
        self,
        actor_state: IndividualState,
        target: ObservedIndividual,
    ) -> bool:
        if actor_state.hunt_cooldown > 0:
            return False

        if not target.alive:
            return False

        if target.id == actor_state.id:
            return False

        return True

    def _hunt_enumeration_enabled(self) -> bool:
        return True

    def _food_ratio(self, food: float, capacity: float) -> float:
        reference = capacity if capacity > 0 else 5.0
        return max(0.0, min(1.0, food / reference))

    def _safe_ratio(self, value: float, maximum: float) -> float:
        if maximum <= 0:
            return 0.0
        return max(0.0, min(1.0, value / maximum))

    def _density_ratio(self, occupant_count: int) -> float:
        return max(0.0, min(1.0, occupant_count / 4.0))
