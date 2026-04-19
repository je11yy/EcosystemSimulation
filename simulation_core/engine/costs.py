from dataclasses import dataclass

from ..agent.actions import ActionOption
from ..agent.state import AgentState
from ..config import SimConfig
from ..enums import AgentActionType


@dataclass(frozen=True)
class ActionCost:
    hunger: float = 0.0
    hp: float = 0.0


class ActionCostCalculator:
    def __init__(self, cfg: SimConfig):
        self.cfg = cfg

    def calculate(self, state: AgentState, action: ActionOption) -> ActionCost:
        hunger_cost = self.cfg.maintenance_hunger_cost + self._base_action_cost(action.type)
        hunger_cost *= state.traits.metabolism
        hunger_cost *= self._trait_cost_multiplier(state, action.type)
        return ActionCost(hunger=max(0, hunger_cost))

    def _base_action_cost(self, action_type: AgentActionType) -> float:
        if action_type == AgentActionType.EAT:
            return self.cfg.eat_hunger_cost
        if action_type == AgentActionType.MOVE:
            return self.cfg.move_hunger_cost
        if action_type == AgentActionType.MATE:
            return self.cfg.mate_hunger_cost
        if action_type == AgentActionType.REST:
            return self.cfg.rest_hunger_cost
        if action_type == AgentActionType.HUNT:
            return self.cfg.hunt_hunger_cost
        raise ValueError(f"Unsupported action type: {action_type}")

    def _trait_cost_multiplier(self, state: AgentState, action_type: AgentActionType) -> float:
        if action_type == AgentActionType.EAT:
            trait_value = state.traits.hunger_drive
        elif action_type == AgentActionType.MOVE:
            return max(
                self.cfg.min_trait_cost_multiplier,
                max(1.0, state.traits.site_fidelity) / max(1.0, state.traits.dispersal_drive),
            )
        elif action_type == AgentActionType.MATE:
            trait_value = state.traits.reproduction_drive
        elif action_type == AgentActionType.HUNT:
            trait_value = state.traits.predation_drive
        else:
            trait_value = 1.0

        return max(self.cfg.min_trait_cost_multiplier, 1.0 / max(1.0, trait_value))


def apply_action_cost(state: AgentState, cost: ActionCost, cfg: SimConfig) -> ActionCost:
    hunger_capacity = max(0, cfg.hunger_max - state.hunger)
    hunger_to_apply = min(cost.hunger, hunger_capacity)
    overflow_hunger = max(0, cost.hunger - hunger_to_apply)
    hp_cost = cost.hp + overflow_hunger * cfg.hunger_overflow_hp_damage_factor

    state.increase_hunger(hunger_to_apply, cfg)
    if hp_cost > 0:
        state.decrease_hp(hp_cost, cfg)

    return ActionCost(hunger=hunger_to_apply, hp=hp_cost)
