from typing import Optional

from ..agent.actions import ActionOption
from ..agent.registry import Agent
from ..config import SimConfig
from ..enums import AgentActionType, AgentSex
from ..genome import GenomeCompatibilityCalculator, GenomeRecombinator
from ..world import WorldState
from .costs import ActionCost, ActionCostCalculator, apply_action_cost
from .logs import AppliedActionResult


class ActionApplier:
    def __init__(self, cfg: SimConfig):
        self.cfg = cfg
        self.cost_calculator = ActionCostCalculator(cfg)
        self.compatibility_calculator = GenomeCompatibilityCalculator()

    def apply_cost(self, agent: Agent, action: ActionOption) -> ActionCost:
        cost = self.cost_calculator.calculate(agent.state, action)
        return apply_action_cost(agent.state, cost, self.cfg)

    def apply_rest(
        self,
        agent: Agent,
        action: ActionOption,
        cost: ActionCost,
    ) -> AppliedActionResult:
        agent.state.increase_hp(self.cfg.rest_hp_recovery, self.cfg)
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=action.type.value,
            success=True,
            hunger_cost=cost.hunger,
            hp_loss=cost.hp,
        )

    def apply_move(
        self,
        agent: Agent,
        action: ActionOption,
        cost: ActionCost,
        world: WorldState,
    ) -> AppliedActionResult:
        if action.to_territory is None:
            return self.failed_result(agent, action, "no_target_territory", cost)

        neighbors = world.get_neighbors(agent.state.location)
        if action.to_territory not in neighbors:
            return self.failed_result(agent, action, "territory_unreachable", cost)

        agent.state.move_to(action.to_territory)
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=action.type.value,
            success=True,
            target_id=str(action.to_territory),
            hunger_cost=cost.hunger,
            hp_loss=cost.hp,
        )

    def apply_mate(
        self,
        agent: Agent,
        action: ActionOption,
        cost: ActionCost,
        agents,
        recombinator: GenomeRecombinator,
        rng,
    ) -> AppliedActionResult:
        if action.partner_id is None:
            return self.failed_result(agent, action, "no_partner", cost)

        partner = _get_alive_agent(agents, action.partner_id)
        if partner is None:
            return self.failed_result(agent, action, "partner_unavailable", cost)
        if partner.state.location != agent.state.location:
            return self.failed_result(agent, action, "partner_on_another_territory", cost)
        if partner.state.sex == agent.state.sex:
            return self.failed_result(agent, action, "same_sex_partner", cost)

        mother, father = _parents(agent, partner)
        if mother.state.is_pregnant:
            return self.failed_result(agent, action, "mother_already_pregnant", cost)
        if not self.compatibility_calculator.is_compatible(
            mother.genome,
            father.genome,
            min_score=self.cfg.mate_genome_compatibility_min_score,
        ):
            return self.failed_result(agent, action, "partner_genome_incompatible", cost)

        child_genome = recombinator.recombine(mother.genome, father.genome, rng).genome
        mother.state.is_pregnant = True
        mother.state.ticks_to_birth = self.cfg.pregnancy_duration_ticks
        mother.pending_child_genome = child_genome
        mother.pending_partner_id = father.state.id

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=action.type.value,
            success=True,
            target_id=str(partner.state.id),
            hunger_cost=cost.hunger,
            hp_loss=cost.hp,
        )

    def apply_hunt(
        self,
        agent: Agent,
        action: ActionOption,
        cost: ActionCost,
        agents,
        rng,
        target_defense_multiplier: Optional[float] = None,
    ) -> AppliedActionResult:
        if action.target_id is None:
            return self.failed_result(agent, action, "no_target", cost)

        target = _get_alive_agent(agents, action.target_id)
        if target is None:
            return self.failed_result(agent, action, "target_unavailable", cost)
        if target.state.location != agent.state.location:
            return self.failed_result(agent, action, "target_on_another_territory", cost)

        attack_score = agent.state.effective_strength * rng.uniform(0.75, 1.25)
        defense_multiplier = target_defense_multiplier or 1.0
        defense_score = (
            target.state.effective_defense * defense_multiplier * rng.uniform(0.75, 1.25)
        )
        success = attack_score >= defense_score

        damage_to_target = 0.0
        damage_to_hunter = 0.0
        hunger_restored = 0.0

        if success:
            damage_to_target = max(
                0.1,
                self.cfg.hunt_base_damage
                + agent.state.effective_strength
                - target.state.effective_defense,
            )
            target.state.decrease_hp(damage_to_target, self.cfg)
            hunger_restored = self.cfg.hunt_success_hunger_restore * max(
                1.0,
                agent.state.traits.carnivore_digestion,
            )
            agent.state.decrease_hunger(hunger_restored, self.cfg)
            agent.state.increase_hp(self.cfg.hunt_success_hp_restore, self.cfg)
        else:
            damage_to_hunter = max(
                0.1,
                self.cfg.hunt_counter_damage
                + target.state.effective_strength
                - agent.state.effective_defense,
            )
            agent.state.decrease_hp(damage_to_hunter, self.cfg)

        agent.state.hunt_cooldown = max(
            self.cfg.hunt_cooldown_ticks + 1,
            agent.state.hunt_cooldown,
        )

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=action.type.value,
            success=success,
            target_id=str(target.state.id),
            hunger_cost=cost.hunger,
            hp_loss=cost.hp + damage_to_hunter,
            hunger_restored=hunger_restored,
            damage_to_target=damage_to_target,
            target_died=not target.state.is_alive,
            actor_died=not agent.state.is_alive,
            actor_death_reason="injury" if not agent.state.is_alive else "",
            target_death_reason="hunted" if not target.state.is_alive else "",
        )

    def apply_defense_reaction(self, target: Agent) -> AppliedActionResult:
        cost = apply_action_cost(
            target.state,
            ActionCost(hunger=self.cfg.defend_hunger_cost),
            self.cfg,
        )
        return AppliedActionResult(
            agent_id=str(target.state.id),
            action_type="defend_from_hunt",
            success=True,
            reason="reactive_defense",
            hunger_cost=cost.hunger,
            hp_loss=cost.hp,
            actor_died=not target.state.is_alive,
            actor_death_reason="exhaustion" if not target.state.is_alive else "",
        )

    def apply_successful_eat(
        self,
        agent: Agent,
        cost: ActionCost,
        world: WorldState,
    ) -> AppliedActionResult:
        territory = world.get_territory(agent.state.location)
        consumed_food = min(self.cfg.food_per_eat, territory.food)
        territory.consume_food(consumed_food)
        agent.state.decrease_hunger(self.cfg.eat_hunger_restore, self.cfg)
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=AgentActionType.EAT.value,
            success=True,
            hunger_cost=cost.hunger,
            hp_loss=cost.hp,
            hunger_restored=self.cfg.eat_hunger_restore,
            consumed_food=consumed_food,
        )

    def failed_result(
        self,
        agent: Agent,
        action: ActionOption,
        reason: str,
        cost=None,
    ) -> AppliedActionResult:
        cost = cost or ActionCost()
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=action.type.value,
            success=False,
            reason=reason,
            hunger_cost=cost.hunger,
            hp_loss=cost.hp,
            actor_died=not agent.state.is_alive,
            actor_death_reason="exhaustion" if not agent.state.is_alive else "",
        )


def _get_alive_agent(agents, agent_id: int):
    try:
        agent = agents.get(agent_id)
    except KeyError:
        return None
    if not agent.state.is_alive:
        return None
    return agent


def _parents(first: Agent, second: Agent) -> tuple[Agent, Agent]:
    if first.state.sex == AgentSex.FEMALE:
        return first, second
    return second, first
