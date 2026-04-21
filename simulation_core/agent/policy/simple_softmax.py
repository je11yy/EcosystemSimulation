import math
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ...enums import AgentActionType
from ..actions import ActionOption, ScoredOption
from ..observation import Observation, ObservedAgent, ObservedTerritory
from .weights import PolicyScoreWeights

if TYPE_CHECKING:
    from ...engine.context import DecisionContext


@dataclass
class SimpleSoftmaxPolicy:
    beta: Optional[float] = None
    weights: PolicyScoreWeights = PolicyScoreWeights()

    def choose_action(
        self,
        context: "DecisionContext",
        rng: Optional[random.Random] = None,
    ) -> ActionOption:
        scored_options = self.score_options(context)
        if not scored_options:
            return ActionOption(type=AgentActionType.REST)

        rng = rng or random.Random()
        beta = self.beta if self.beta is not None else context.cost_calculator.cfg.beta_default
        weights = self._softmax_weights(scored_options, beta)
        roll = rng.random()
        cumulative = 0.0

        for index, scored_option in enumerate(scored_options):
            cumulative += weights[index]
            if roll <= cumulative:
                return scored_option.option

        return scored_options[-1].option

    def enumerate_options(self, context: "DecisionContext") -> list[ActionOption]:
        agent = context.agent
        options = [ActionOption(type=AgentActionType.REST)]

        eat_option = ActionOption(type=AgentActionType.EAT)
        if (
            context.current_location.food
            >= context.cost_calculator.calculate(agent.state, eat_option).hunger
        ):
            options.append(eat_option)

        for territory in context.observation.neighboring_territories:
            if territory.id == agent.state.location:
                continue
            options.append(ActionOption(type=AgentActionType.MOVE, to_territory=territory.id))

        if not agent.state.is_pregnant:
            options.extend(self._mate_options(context))

        if agent.state.hunt_cooldown == 0:
            options.extend(self._hunt_options(context))

        return options

    def score_options(self, context: "DecisionContext") -> list[ScoredOption]:
        return [
            ScoredOption(option=option, utility=self.score_single_option(context, option))
            for option in self.enumerate_options(context)
        ]

    def should_accept_mate_request(
        self,
        context: "DecisionContext",
        partner_id: int,
    ) -> bool:
        hunger_pressure = self._ratio(
            context.agent.state.hunger,
            context.cost_calculator.cfg.hunger_max,
        )
        if hunger_pressure > context.cost_calculator.cfg.mate_reconsider_hunger_threshold:
            return False

        mate_option = ActionOption(type=AgentActionType.MATE, partner_id=partner_id)
        if mate_option not in self._mate_options(context):
            return False

        mate_score = self.score_single_option(context, mate_option)
        rest_score = self.score_single_option(
            context,
            ActionOption(type=AgentActionType.REST),
        )
        return mate_score >= rest_score - context.cost_calculator.cfg.mate_reconsider_score_margin

    def score_single_option(self, context: "DecisionContext", option: ActionOption) -> float:
        if option.type == AgentActionType.EAT:
            utility = self.score_eat(context)
        elif option.type == AgentActionType.MOVE:
            utility = self.score_move(context, option)
        elif option.type == AgentActionType.MATE:
            utility = self.score_mate(context, option)
        elif option.type == AgentActionType.HUNT:
            utility = self.score_hunt(context, option)
        elif option.type == AgentActionType.REST:
            utility = self.score_rest(context)
        else:
            raise ValueError(f"Unsupported action type: {option.type}")

        return utility - self._cost_penalty(context, option)

    def score_eat(self, context: "DecisionContext") -> float:
        agent = context.agent
        traits = agent.state.traits
        hunger_need = self._ratio(agent.state.hunger, context.cost_calculator.cfg.hunger_max)
        local_food_ratio = self._ratio(
            context.current_location.food,
            context.current_location.food_capacity,
        )
        local_density_pressure = self._density_pressure(
            context.observation.current_territory.occupant_count,
            traits.social_tolerance,
        )

        return (
            hunger_need * self.weights.eat.hunger_need
            + local_food_ratio * self.weights.eat.local_food
            + (1 - local_density_pressure) * self.weights.eat.low_density
            + min(1.0, traits.hunger_drive / 3) * self.weights.eat.hunger_drive
        )

    def score_move(self, context: "DecisionContext", option: ActionOption) -> float:
        target = self._find_territory(context.observation, option.to_territory)
        if target is None:
            return -1.0

        agent = context.agent
        traits = agent.state.traits
        hunger_need = self._ratio(agent.state.hunger, context.cost_calculator.cfg.hunger_max)
        food_gain = self._ratio(
            target.food,
            target.food + context.current_location.food,
        )
        density_pressure = self._density_pressure(
            context.observation.current_territory.occupant_count,
            traits.social_tolerance,
        )
        target_density = self._density_pressure(target.occupant_count + 1, traits.social_tolerance)
        temperature_fit = self._temperature_fit(
            agent.state.base_temp_pref,
            target.temperature,
            traits,
        )
        movement_cost_penalty = self._ratio(target.movement_cost, target.movement_cost + 1)

        return (
            hunger_need * food_gain * self.weights.move.food_gain_when_hungry
            + density_pressure * self.weights.move.current_density_pressure
            + temperature_fit * self.weights.move.temperature_fit
            + min(1.0, traits.dispersal_drive / 3) * self.weights.move.dispersal_drive
            - min(1.0, traits.site_fidelity / 3) * self.weights.move.site_fidelity_penalty
            - target_density * self.weights.move.target_density_penalty
            - movement_cost_penalty * self.weights.move.movement_cost_penalty
        )

    def score_mate(self, context: "DecisionContext", option: ActionOption) -> float:
        partner = self._find_agent(context.observation, option.partner_id)
        if partner is None:
            return -1.0

        agent = context.agent
        hp_ratio = self._ratio(agent.state.hp, agent.state.max_hp)
        hunger_pressure = self._ratio(agent.state.hunger, context.cost_calculator.cfg.hunger_max)
        satisfaction = self._ratio(agent.state.satisfaction, 5)
        partner_health = self._ratio(partner.hp, agent.state.max_hp)

        return (
            min(1.0, agent.state.traits.reproduction_drive / 3)
            * self.weights.mate.reproduction_drive
            + satisfaction * self.weights.mate.satisfaction
            + hp_ratio * self.weights.mate.own_health
            + partner_health * self.weights.mate.partner_health
            - hunger_pressure * self.weights.mate.hunger_penalty
        )

    def score_hunt(self, context: "DecisionContext", option: ActionOption) -> float:
        target = self._find_agent(context.observation, option.target_id)
        if target is None:
            return -1.0

        agent = context.agent
        hunger_pressure = self._ratio(agent.state.hunger, context.cost_calculator.cfg.hunger_max)
        attack_advantage = self._ratio(
            agent.state.effective_strength,
            agent.state.effective_strength + target.defense,
        )
        target_weakness = 1 - self._ratio(target.hp, agent.state.max_hp)

        return (
            hunger_pressure * self.weights.hunt.hunger_pressure
            + min(1.0, agent.state.traits.predation_drive / 3) * self.weights.hunt.predation_drive
            + min(1.0, agent.state.traits.aggression_drive / 3) * self.weights.hunt.aggression_drive
            + attack_advantage * self.weights.hunt.attack_advantage
            + target_weakness * self.weights.hunt.target_weakness
        )

    def score_rest(self, context: "DecisionContext") -> float:
        agent = context.agent
        hp_need = 1 - self._ratio(agent.state.hp, agent.state.max_hp)
        hunger_pressure = self._ratio(agent.state.hunger, context.cost_calculator.cfg.hunger_max)
        return (
            hp_need * self.weights.rest.hp_need
            + min(1.0, agent.state.traits.site_fidelity / 3) * self.weights.rest.site_fidelity
            - hunger_pressure * self.weights.rest.hunger_penalty
        )

    def _mate_options(self, context: "DecisionContext") -> list[ActionOption]:
        return [
            ActionOption(type=AgentActionType.MATE, partner_id=partner.id)
            for partner in context.observation.agents
            if partner.is_alive
            and partner.sex != context.agent.state.sex
            and partner.id != context.agent.state.id
        ]

    def _hunt_options(self, context: "DecisionContext") -> list[ActionOption]:
        current_food_ratio = self._ratio(
            context.current_location.food,
            context.current_location.food_capacity,
        )
        hunger_pressure = self._ratio(
            context.agent.state.hunger,
            context.cost_calculator.cfg.hunger_max,
        )
        predation_drive = context.agent.state.traits.predation_drive

        if predation_drive <= 0:
            return []
        if predation_drive < 1.05:
            return []
        if hunger_pressure < 0.4 and current_food_ratio > 0.55 and predation_drive < 1.3:
            return []

        return [
            ActionOption(type=AgentActionType.HUNT, target_id=target.id)
            for target in context.observation.agents
            if target.is_alive and target.id != context.agent.state.id
        ]

    def _cost_penalty(self, context: "DecisionContext", option: ActionOption) -> float:
        cost = context.cost_calculator.calculate(context.agent.state, option)
        hunger_penalty = self._ratio(cost.hunger, context.cost_calculator.cfg.hunger_max)
        hp_penalty = self._ratio(cost.hp, context.agent.state.max_hp)
        return (
            hunger_penalty * self.weights.cost_penalty.hunger
            + hp_penalty * self.weights.cost_penalty.hp
        )

    def _softmax_weights(self, scored_options: list[ScoredOption], beta: float) -> list[float]:
        max_utility = max(scored_option.utility for scored_option in scored_options)
        exp_values = [
            math.exp((scored_option.utility - max_utility) * beta)
            for scored_option in scored_options
        ]
        total = sum(exp_values)
        if total == 0:
            return [1 / len(scored_options)] * len(scored_options)
        return [value / total for value in exp_values]

    def _find_agent(
        self,
        observation: Observation,
        agent_id: Optional[int],
    ) -> Optional[ObservedAgent]:
        if agent_id is None:
            return None
        for agent in observation.agents:
            if agent.id == agent_id:
                return agent
        return None

    def _find_territory(
        self,
        observation: Observation,
        territory_id: Optional[int],
    ) -> Optional[ObservedTerritory]:
        if territory_id is None:
            return None
        for territory in observation.neighboring_territories:
            if territory.id == territory_id:
                return territory
        return None

    def _temperature_fit(self, preferred_temperature: float, temperature: float, traits) -> float:
        delta = temperature - preferred_temperature
        resistance = traits.heat_resistance if delta > 0 else traits.cold_resistance
        adjusted_delta = max(0.0, abs(delta) - resistance)
        return 1 - self._ratio(adjusted_delta, adjusted_delta + 10)

    def _density_pressure(self, occupant_count: int, social_tolerance: float) -> float:
        comfortable_count = 3 + max(0, social_tolerance)
        return self._ratio(occupant_count, comfortable_count)

    def _ratio(self, value: float, max_value: float) -> float:
        if max_value <= 0:
            return 0.0
        return max(0.0, min(1.0, value / max_value))
