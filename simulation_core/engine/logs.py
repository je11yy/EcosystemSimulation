from dataclasses import dataclass, field
from typing import Optional

from ..agent.actions import ActionOption
from .costs import ActionCost


@dataclass(frozen=True)
class Decision:
    tick: int
    agent_id: str
    chosen: ActionOption
    cost: ActionCost = field(default_factory=ActionCost)


@dataclass(frozen=True)
class AppliedActionResult:
    agent_id: str
    action_type: str
    success: bool
    reason: str = ""
    target_id: Optional[str] = None
    hp_loss: float = 0.0
    hunger_cost: float = 0.0
    hunger_restored: float = 0.0
    consumed_food: float = 0.0
    damage_to_target: float = 0.0
    target_died: bool = False
    actor_died: bool = False
    actor_death_reason: str = ""
    target_death_reason: str = ""


@dataclass(frozen=True)
class DeathResult:
    agent_id: str
    reason: str
    tick: int


@dataclass(frozen=True)
class BirthResult:
    parent_id: str
    child_id: str
    tick: int


@dataclass(frozen=True)
class FightEvent:
    territory_id: str
    winner_id: str
    loser_id: str
    loser_hp_loss: float


@dataclass(frozen=True)
class HuntEvent:
    territory_id: str
    hunter_id: str
    target_id: str
    success: bool
    damage_to_target: float
    damage_to_hunter: float
    target_died: bool
    hunter_died: bool
    hunger_restored: float


@dataclass(frozen=True)
class Metrics:
    alive_population: int
    avg_hunger: float
    occupancy_by_territory: dict[str, int]
    deaths_by_reason: dict[str, int]
    successful_hunts: int
    unsuccessful_hunts: int
    consumed_food: float


@dataclass(frozen=True)
class Step:
    eat: int
    move: int
    mate: int
    rest: int
    hunt: int

    deaths: int
    births: int
    fights: int


@dataclass(frozen=True)
class Log:
    tick: int
    decisions: list[Decision]
    step_result: Step
    metrics: Metrics


@dataclass(frozen=True)
class StepResult:
    tick: int
    decisions: list[Decision]
    applied_results: list[AppliedActionResult]
    deaths: list[DeathResult]
    births: list[BirthResult]
    fights: list[FightEvent]
    hunts: list[HuntEvent]
    metrics: Metrics
    metrics_history: list[Metrics]

    @property
    def step(self) -> Step:
        return Step(
            eat=sum(1 for decision in self.decisions if decision.chosen.type.value == "eat"),
            move=sum(1 for decision in self.decisions if decision.chosen.type.value == "move"),
            mate=sum(1 for decision in self.decisions if decision.chosen.type.value == "mate"),
            rest=sum(1 for decision in self.decisions if decision.chosen.type.value == "rest"),
            hunt=sum(1 for decision in self.decisions if decision.chosen.type.value == "hunt"),
            deaths=len(self.deaths),
            births=len(self.births),
            fights=len(self.fights),
        )
