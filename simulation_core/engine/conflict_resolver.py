from collections import defaultdict
from typing import DefaultDict

from ..agent.actions import ActionOption
from ..agent.registry import Agent
from ..config import SimConfig
from ..enums import AgentActionType
from ..world import WorldState
from .applier import ActionApplier
from .costs import ActionCost
from .logs import AppliedActionResult, FightEvent

EatClaims = DefaultDict[int, list[tuple[Agent, ActionCost]]]


class FoodConflictResolver:
    def __init__(self, cfg: SimConfig, applier: ActionApplier):
        self.cfg = cfg
        self.applier = applier

    def empty_claims(self) -> EatClaims:
        return defaultdict(list)

    def resolve(
        self,
        claims: EatClaims,
        world: WorldState,
        rng,
    ) -> tuple[list[AppliedActionResult], list[FightEvent]]:
        applied_results: list[AppliedActionResult] = []
        fights: list[FightEvent] = []

        for territory_id, contenders in claims.items():
            territory = world.get_territory(territory_id)
            alive_contenders = [(agent, cost) for agent, cost in contenders if agent.state.is_alive]
            if not alive_contenders:
                continue

            available_units = int(territory.food // self.cfg.food_per_eat)
            if available_units <= 0:
                for agent, cost in alive_contenders:
                    applied_results.append(
                        self.applier.failed_result(
                            agent,
                            ActionOption(AgentActionType.EAT),
                            "no_food",
                            cost,
                        )
                    )
                continue

            if available_units >= len(alive_contenders):
                for agent, cost in alive_contenders:
                    applied_results.append(self.applier.apply_successful_eat(agent, cost, world))
                continue

            winners = self._select_winners(alive_contenders, available_units, rng)
            winner_ids = {winner.state.id for winner, _cost in winners}

            for winner, cost in winners:
                applied_results.append(self.applier.apply_successful_eat(winner, cost, world))

            for loser, cost in alive_contenders:
                if loser.state.id in winner_ids:
                    continue

                winner, _winner_cost = rng.choice(winners)
                hp_loss = self._fight_damage(winner, loser)
                loser.state.decrease_hp(hp_loss, self.cfg)
                fights.append(
                    FightEvent(
                        territory_id=str(territory_id),
                        winner_id=str(winner.state.id),
                        loser_id=str(loser.state.id),
                        loser_hp_loss=hp_loss,
                    )
                )
                applied_results.append(
                    AppliedActionResult(
                        agent_id=str(loser.state.id),
                        action_type="fight_loss",
                        success=True,
                        hp_loss=hp_loss,
                        hunger_cost=cost.hunger,
                        actor_died=not loser.state.is_alive,
                        actor_death_reason="injury" if not loser.state.is_alive else "",
                    )
                )

        return applied_results, fights

    def _select_winners(
        self,
        contenders: list[tuple[Agent, ActionCost]],
        count: int,
        rng,
    ) -> list[tuple[Agent, ActionCost]]:
        ranked = sorted(
            contenders,
            key=lambda item: (
                item[0].state.effective_strength + item[0].state.effective_defense + rng.random()
            ),
            reverse=True,
        )
        return ranked[:count]

    def _fight_damage(self, winner: Agent, loser: Agent) -> float:
        return max(
            0.1,
            self.cfg.fight_damage_base
            + winner.state.effective_strength
            - loser.state.effective_defense,
        )
