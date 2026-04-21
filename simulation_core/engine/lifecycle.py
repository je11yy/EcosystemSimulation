from ..agent import AgentState
from ..agent.registry import AgentRegistry
from ..config import SimConfig
from ..enums import AgentSex
from .logs import AppliedActionResult, BirthResult, DeathResult


class LifecycleResolver:
    def __init__(self, cfg: SimConfig, dead_agent_ids: set[int]):
        self.cfg = cfg
        self.dead_agent_ids = dead_agent_ids

    def resolve_births(self, agents: AgentRegistry, rng, tick: int) -> list[BirthResult]:
        births = []
        for agent in list(agents.all()):
            if not agent.state.is_alive or not agent.state.is_pregnant:
                continue

            agent.state.ticks_to_birth -= 1
            if agent.state.ticks_to_birth > 0:
                continue

            if agent.pending_child_genome is None:
                agent.state.is_pregnant = False
                continue

            child_id = self._next_agent_id(agents)
            child_state = AgentState(
                id=child_id,
                sex=rng.choice([AgentSex.MALE, AgentSex.FEMALE]),
                hunger=self.cfg.newborn_hunger,
                hp=self.cfg.newborn_hp,
                is_pregnant=False,
                ticks_to_birth=0,
                satisfaction=self.cfg.newborn_satisfaction,
                hunt_cooldown=0,
                base_strength=agent.state.base_strength,
                base_defense=agent.state.base_defense,
                base_temp_pref=agent.state.base_temp_pref,
                location=agent.state.location,
            )
            agents.add(child_state, agent.pending_child_genome)

            births.append(
                BirthResult(
                    parent_id=str(agent.state.id),
                    child_id=str(child_id),
                    tick=tick,
                    partner_id=(
                        str(agent.pending_partner_id)
                        if agent.pending_partner_id is not None
                        else None
                    ),
                )
            )
            agent.state.is_pregnant = False
            agent.state.ticks_to_birth = 0
            agent.pending_child_genome = None
            agent.pending_partner_id = None

        return births

    def apply_starvation_damage(
        self,
        agents: AgentRegistry,
        tick: int,
    ) -> list[DeathResult]:
        deaths = []
        for agent in agents.all():
            if not agent.state.is_alive:
                continue
            if agent.state.hunger < self.cfg.hunger_max:
                continue

            agent.state.decrease_hp(self.cfg.starvation_hp_damage, self.cfg)
            if not agent.state.is_alive and agent.state.id not in self.dead_agent_ids:
                self.dead_agent_ids.add(agent.state.id)
                deaths.append(
                    DeathResult(
                        agent_id=str(agent.state.id),
                        reason="starvation",
                        tick=tick,
                    )
                )

        return deaths

    def collect_new_deaths(
        self,
        agents: AgentRegistry,
        tick: int,
        applied_results: list[AppliedActionResult],
    ) -> list[DeathResult]:
        death_reasons = self._death_reasons_from_results(applied_results)
        deaths = []

        for agent in agents.all():
            if agent.state.is_alive or agent.state.id in self.dead_agent_ids:
                continue

            self.dead_agent_ids.add(agent.state.id)
            deaths.append(
                DeathResult(
                    agent_id=str(agent.state.id),
                    reason=death_reasons.get(str(agent.state.id), "hp_depleted"),
                    tick=tick,
                )
            )

        return deaths

    def decay_hunt_cooldowns(self, agents: AgentRegistry) -> None:
        for agent in agents.all():
            if agent.state.hunt_cooldown > 0:
                agent.state.hunt_cooldown -= 1

    def _death_reasons_from_results(
        self,
        applied_results: list[AppliedActionResult],
    ) -> dict[str, str]:
        reasons = {}

        for result in applied_results:
            if result.actor_died:
                reasons[result.agent_id] = result.actor_death_reason or _fallback_actor_reason(
                    result
                )
            if result.target_died and result.target_id is not None:
                reasons[result.target_id] = result.target_death_reason or "injury"

        return reasons

    def _next_agent_id(self, agents: AgentRegistry) -> int:
        if not agents.agents:
            return 1
        return max(agents.agents) + 1


def _fallback_actor_reason(result: AppliedActionResult) -> str:
    if result.reason == "exhaustion":
        return "exhaustion"
    if result.action_type in {"hunt", "fight_loss"}:
        return "injury"
    return "hp_depleted"
