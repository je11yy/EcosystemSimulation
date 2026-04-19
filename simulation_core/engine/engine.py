import random

from ..agent import SimpleSoftmaxPolicy
from ..agent.actions import ActionOption
from ..agent.observer import AgentObserver
from ..agent.registry import Agent, AgentRegistry
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
        self.rng = random.Random()
        self.tick = 0
        self.logs: list[Log] = []
        self.metrics_history: list[Metrics] = []
        self.dead_agent_ids: set[int] = set()
        self.lifecycle_resolver = LifecycleResolver(self.cfg, self.dead_agent_ids)
        self.metrics_collector = MetricsCollector()

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

    def apply_action_cost(self, agent_id, action):
        agent = self.agents.get(agent_id)
        return self.action_applier.apply_cost(agent, action)

    def regenerate_territories(self):
        self.world.regenerate_food()

    def step(self) -> StepResult:
        self.refresh_agents()

        decisions: list[Decision] = []
        applied_results: list[AppliedActionResult] = []
        fights: list[FightEvent] = []
        hunts: list[HuntEvent] = []
        deaths: list[DeathResult] = []
        births: list[BirthResult] = []
        decision_buffer: list[tuple[Agent, ActionOption]] = []

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
            decision_buffer.append((agent, chosen))

        eat_claims = self._apply_non_eat_actions(decision_buffer, applied_results, hunts)
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

    def _apply_non_eat_actions(
        self,
        decision_buffer: list[tuple[Agent, ActionOption]],
        applied_results: list[AppliedActionResult],
        hunts: list[HuntEvent],
    ) -> EatClaims:
        eat_claims = self.food_conflict_resolver.empty_claims()

        for agent, action in decision_buffer:
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

            if action.type == AgentActionType.EAT:
                eat_claims[agent.state.location].append((agent, cost))
                continue

            if action.type == AgentActionType.REST:
                applied_results.append(self.action_applier.apply_rest(agent, action, cost))
            elif action.type == AgentActionType.MOVE:
                applied_results.append(
                    self.action_applier.apply_move(agent, action, cost, self.world)
                )
            elif action.type == AgentActionType.MATE:
                applied_results.append(
                    self.action_applier.apply_mate(
                        agent,
                        action,
                        cost,
                        self.agents,
                        self.recombinator,
                        self.rng,
                    )
                )
            elif action.type == AgentActionType.HUNT:
                result = self.action_applier.apply_hunt(
                    agent,
                    action,
                    cost,
                    self.agents,
                    self.rng,
                )
                applied_results.append(result)
                if action.target_id is not None:
                    hunts.append(
                        HuntEvent(
                            territory_id=str(agent.state.location),
                            hunter_id=str(agent.state.id),
                            target_id=str(action.target_id),
                            success=result.success,
                            damage_to_target=result.damage_to_target,
                            damage_to_hunter=result.hp_loss,
                            target_died=result.target_died,
                            hunter_died=result.actor_died,
                            hunger_restored=result.hunger_restored,
                        )
                    )
            else:
                applied_results.append(
                    self.action_applier.failed_result(agent, action, "unsupported_action")
                )

        return eat_claims
