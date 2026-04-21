import random
from collections import defaultdict

from ..agent.actions import ActionOption
from ..agent.observer import AgentObserver
from ..agent.policy.simple_softmax import SimpleSoftmaxPolicy
from ..agent.registry import AgentRegistry
from ..config import SimConfig
from ..enums import AgentActionType
from ..genome import GenomeRecombinator
from ..world import WorldState
from .applier import ActionApplier
from .conflict_resolver import EatClaims, FoodConflictResolver
from .context import DecisionContext
from .lifecycle import LifecycleResolver
from .logs import (
    AppliedActionResult,
    BirthResult,
    DeathResult,
    Decision,
    FightEvent,
    HuntEvent,
    Log,
    Metrics,
    StepResult,
)
from .metrics import MetricsCollector
from .satisfaction import SatisfactionUpdater


class Engine:
    def __init__(self, cfg=None):
        self.cfg = cfg or SimConfig()
        self.world = WorldState()
        self.agents = AgentRegistry(self.cfg)
        self.action_applier = ActionApplier(self.cfg)
        self.food_conflict_resolver = FoodConflictResolver(self.cfg, self.action_applier)
        self.observer = AgentObserver()
        self.policy = SimpleSoftmaxPolicy()
        self.recombinator = GenomeRecombinator()
        self.rng = random.Random(self.cfg.random_seed)
        self.tick = 0
        self.logs: list[Log] = []
        self.metrics_history: list[Metrics] = []
        self.dead_agent_ids: set[int] = set()
        self.lifecycle_resolver = LifecycleResolver(self.cfg, self.dead_agent_ids)
        self.metrics_collector = MetricsCollector()
        self.satisfaction_updater = SatisfactionUpdater(self.cfg)

    def add_agent(self, state, genome):
        self.agents.add(state, genome)
        self.refresh_agent(state.id)

    def build_decision_context(self, agent_id):
        self.refresh_agents()
        agent = self.agents.get(agent_id)
        return self._build_decision_context(agent)

    def _build_decision_context(self, agent):
        observation = self.observer.build(agent, self.world, self.agents)
        return DecisionContext(
            agent=agent,
            agents=self.agents,
            world=self.world,
            observation=observation,
            cost_calculator=self.action_applier.cost_calculator,
        )

    def refresh_agent(self, agent_id):
        agent = self.agents.get(agent_id)
        if agent.state.location not in self.world.territories:
            return
        observation = self.observer.build(agent, self.world, self.agents)
        agent.refresh_gene_effects(self.cfg, observation)

    def refresh_agents(self):
        for agent in self.agents.all():
            self.refresh_agent(agent.state.id)

    def update_satisfaction(self):
        self.refresh_agents()
        self.satisfaction_updater.update(self.agents, self.world)

    def apply_action_cost(self, agent_id, action):
        agent = self.agents.get(agent_id)
        return self.action_applier.apply_cost(agent, action)

    def regenerate_territories(self):
        self.world.regenerate_food()

    def step(self) -> StepResult:
        # Решения используют удовлетворенность, рассчитанную на предыдущем тике.
        # Новая удовлетворенность считается ниже как результат текущего шага.
        self.refresh_agents()

        decisions: list[Decision] = []
        applied_results: list[AppliedActionResult] = []
        fights: list[FightEvent] = []
        hunts: list[HuntEvent] = []
        deaths: list[DeathResult] = []
        births: list[BirthResult] = []
        decisions_by_agent_id: dict[int, ActionOption] = {}

        for agent in self.agents.all():
            if not agent.state.is_alive:
                continue

            context = self._build_decision_context(agent)
            chosen = self.policy.choose_action(context, self.rng)
            cost = self.action_applier.cost_calculator.calculate(agent.state, chosen)
            decisions.append(
                Decision(
                    tick=self.tick,
                    agent_id=str(agent.state.id),
                    chosen=chosen,
                    cost=cost,
                )
            )
            decisions_by_agent_id[agent.state.id] = chosen

        eat_claims = self._resolve_actions(
            decisions_by_agent_id,
            applied_results,
            hunts,
        )
        eat_results, fight_events = self.food_conflict_resolver.resolve(
            eat_claims,
            self.world,
            self.rng,
        )
        applied_results.extend(eat_results)
        fights.extend(fight_events)

        deaths.extend(
            self.lifecycle_resolver.collect_new_deaths(
                self.agents,
                self.tick,
                applied_results,
            )
        )
        births.extend(self.lifecycle_resolver.resolve_births(self.agents, self.rng, self.tick))
        deaths.extend(self.lifecycle_resolver.apply_starvation_damage(self.agents, self.tick))
        self.lifecycle_resolver.decay_hunt_cooldowns(self.agents)
        self.regenerate_territories()
        self.update_satisfaction()
        self.refresh_agents()

        metrics = self.metrics_collector.collect(
            self.agents,
            deaths,
            hunts,
            applied_results,
        )
        self.metrics_history.append(metrics)

        result = StepResult(
            tick=self.tick,
            decisions=decisions,
            applied_results=applied_results,
            deaths=deaths,
            births=births,
            fights=fights,
            hunts=hunts,
            metrics=metrics,
            metrics_history=list(self.metrics_history),
        )
        self.logs.append(
            Log(
                tick=self.tick,
                decisions=decisions,
                step_result=result.step,
                metrics=metrics,
            )
        )
        self.tick += 1
        return result

    def _resolve_actions(
        self,
        decisions_by_agent_id: dict[int, ActionOption],
        applied_results: list[AppliedActionResult],
        hunts: list[HuntEvent],
    ) -> EatClaims:
        eat_claims = self.food_conflict_resolver.empty_claims()
        consumed_agent_ids: set[int] = set()

        self._resolve_hunts(
            decisions_by_agent_id,
            applied_results,
            hunts,
            consumed_agent_ids,
        )
        self._resolve_mutual_mates(
            decisions_by_agent_id,
            applied_results,
            consumed_agent_ids,
        )

        for agent_id, action in decisions_by_agent_id.items():
            if agent_id in consumed_agent_ids:
                continue
            agent = self.agents.get(agent_id)
            if not agent.state.is_alive:
                applied_results.append(
                    self.action_applier.failed_result(
                        agent,
                        action,
                        "dead_before_resolution",
                    )
                )
                continue

            cost = self.action_applier.apply_cost(agent, action)
            if not agent.state.is_alive:
                applied_results.append(
                    self.action_applier.failed_result(
                        agent,
                        action,
                        "exhaustion",
                        cost,
                    )
                )
                continue

            if action.type == AgentActionType.MATE:
                applied_results.append(
                    self.action_applier.failed_result(
                        agent,
                        action,
                        "partner_not_reciprocating",
                        cost,
                    )
                )
                continue

            if action.type == AgentActionType.HUNT:
                applied_results.append(
                    self.action_applier.failed_result(
                        agent,
                        action,
                        "target_not_engaged",
                        cost,
                    )
                )
                continue

            if action.type == AgentActionType.EAT:
                eat_claims[agent.state.location].append((agent, cost))
                continue

            if action.type == AgentActionType.REST:
                applied_results.append(self.action_applier.apply_rest(agent, action, cost))
            elif action.type == AgentActionType.MOVE:
                applied_results.append(
                    self.action_applier.apply_move(agent, action, cost, self.world)
                )
            else:
                applied_results.append(
                    self.action_applier.failed_result(agent, action, "unsupported_action")
                )

        return eat_claims

    def _resolve_mutual_mates(
        self,
        decisions_by_agent_id: dict[int, ActionOption],
        applied_results: list[AppliedActionResult],
        consumed_agent_ids: set[int],
    ) -> None:
        for agent_id, action in decisions_by_agent_id.items():
            if action.type != AgentActionType.MATE or agent_id in consumed_agent_ids:
                continue
            if action.partner_id is None:
                continue
            if action.partner_id in consumed_agent_ids:
                continue

            partner_action = decisions_by_agent_id.get(action.partner_id)
            is_mutual = (
                partner_action is not None
                and partner_action.type == AgentActionType.MATE
                and partner_action.partner_id == agent_id
            )
            if not is_mutual and not self._should_accept_mate_request(action.partner_id, agent_id):
                continue

            if (
                partner_action is None
                or partner_action.type != AgentActionType.MATE
                or partner_action.partner_id != agent_id
            ) and not is_mutual:
                applied_results.append(
                    AppliedActionResult(
                        agent_id=str(action.partner_id),
                        action_type=partner_action.type.value if partner_action else "rest",
                        success=False,
                        reason="replaced_by_mate_reconsideration",
                    )
                )

            agent = self.agents.get(agent_id)
            partner = self.agents.get(action.partner_id)
            if not agent.state.is_alive or not partner.state.is_alive:
                continue

            agent_cost = self.action_applier.apply_cost(agent, action)
            if not agent.state.is_alive:
                applied_results.append(
                    self.action_applier.failed_result(
                        agent,
                        action,
                        "exhaustion",
                        agent_cost,
                    )
                )
                consumed_agent_ids.add(agent_id)
                continue

            partner_cost = self.action_applier.apply_cost(partner, partner_action)
            if not partner.state.is_alive:
                applied_results.append(
                    self.action_applier.failed_result(
                        partner,
                        partner_action,
                        "exhaustion",
                        partner_cost,
                    )
                )
                consumed_agent_ids.update({agent_id, action.partner_id})
                applied_results.append(
                    self.action_applier.failed_result(
                        agent,
                        action,
                        "partner_exhausted",
                        agent_cost,
                    )
                )
                continue

            applied_results.append(
                self.action_applier.apply_mate(
                    agent,
                    action,
                    agent_cost,
                    self.agents,
                    self.recombinator,
                    self.rng,
                )
            )
            applied_results.append(
                AppliedActionResult(
                    agent_id=str(partner.state.id),
                    action_type=AgentActionType.MATE.value,
                    success=True,
                    target_id=str(agent.state.id),
                    hunger_cost=partner_cost.hunger,
                    hp_loss=partner_cost.hp,
                    reason="mutual_mate_confirmed" if is_mutual else "mate_reconsidered",
                )
            )
            consumed_agent_ids.update({agent_id, action.partner_id})

    def _should_accept_mate_request(self, agent_id: int, partner_id: int) -> bool:
        if agent_id in self.agents.agents:
            agent = self.agents.get(agent_id)
        else:
            return False
        if not agent.state.is_alive:
            return False

        context = self._build_decision_context(agent)
        return self.policy.should_accept_mate_request(context, partner_id)

    def _resolve_hunts(
        self,
        decisions_by_agent_id: dict[int, ActionOption],
        applied_results: list[AppliedActionResult],
        hunts: list[HuntEvent],
        consumed_agent_ids: set[int],
    ) -> None:
        hunts_by_target: dict[int, list[tuple[int, ActionOption]]] = defaultdict(list)
        for agent_id, action in decisions_by_agent_id.items():
            if action.type != AgentActionType.HUNT or action.target_id is None:
                continue
            hunts_by_target[action.target_id].append((agent_id, action))

        for target_id, hunter_entries in hunts_by_target.items():
            if target_id in consumed_agent_ids:
                continue

            try:
                target = self.agents.get(target_id)
            except KeyError:
                continue
            if not target.state.is_alive:
                continue

            original_target_action = decisions_by_agent_id.get(target_id)
            if original_target_action is not None:
                consumed_agent_ids.add(target_id)
                applied_results.append(
                    AppliedActionResult(
                        agent_id=str(target.state.id),
                        action_type=original_target_action.type.value,
                        success=False,
                        reason="replaced_by_defense",
                    )
                )
            applied_results.append(self.action_applier.apply_defense_reaction(target))

            for hunter_id, action in sorted(hunter_entries, key=lambda item: item[0]):
                if hunter_id in consumed_agent_ids:
                    continue
                hunter = self.agents.get(hunter_id)
                if not hunter.state.is_alive:
                    applied_results.append(
                        self.action_applier.failed_result(
                            hunter,
                            action,
                            "dead_before_resolution",
                        )
                    )
                    consumed_agent_ids.add(hunter_id)
                    continue

                if not target.state.is_alive or hunter.state.location != target.state.location:
                    applied_results.append(
                        self.action_applier.failed_result(
                            hunter,
                            action,
                            "target_unavailable",
                        )
                    )
                    consumed_agent_ids.add(hunter_id)
                    continue

                cost = self.action_applier.apply_cost(hunter, action)
                if not hunter.state.is_alive:
                    applied_results.append(
                        self.action_applier.failed_result(
                            hunter,
                            action,
                            "exhaustion",
                            cost,
                        )
                    )
                    consumed_agent_ids.add(hunter_id)
                    continue

                result = self.action_applier.apply_hunt(
                    hunter,
                    action,
                    cost,
                    self.agents,
                    self.rng,
                    target_defense_multiplier=self.cfg.hunt_defense_reaction_multiplier,
                )
                applied_results.append(result)
                consumed_agent_ids.add(hunter_id)
                hunts.append(
                    HuntEvent(
                        territory_id=str(hunter.state.location),
                        hunter_id=str(hunter.state.id),
                        target_id=str(target.state.id),
                        success=result.success,
                        damage_to_target=result.damage_to_target,
                        damage_to_hunter=result.hp_loss,
                        target_died=result.target_died,
                        hunter_died=result.actor_died,
                        hunger_restored=result.hunger_restored,
                    )
                )

                if not target.state.is_alive:
                    break
