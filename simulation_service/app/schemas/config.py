from pydantic import BaseModel


class RuntimeSimConfig(BaseModel):
    hunger_min: int = 0
    hunger_max: int = 5
    strength_min: int = 1
    strength_max: int = 5
    defense_min: int = 1
    defense_max: int = 5
    hp_min: int = 0
    hp_max: int = 5

    beta_default: float = 2.0
    pregnancy_duration_ticks: int = 3
    hunt_cooldown_ticks: int = 1
    newborn_hp: float = 3.0
    newborn_hunger: float = 1.0
    newborn_satisfaction: float = 3.0

    maintenance_hunger_cost: float = 0.1
    eat_hunger_cost: float = 0.2
    move_hunger_cost: float = 0.5
    mate_hunger_cost: float = 1.0
    rest_hunger_cost: float = 0.05
    hunt_hunger_cost: float = 0.8
    hunger_overflow_hp_damage_factor: float = 1.0
    min_trait_cost_multiplier: float = 0.25

    food_per_eat: float = 1.0
    eat_hunger_restore: float = 1.5
    rest_hp_recovery: float = 0.2
    hunt_base_damage: float = 1.0
    hunt_counter_damage: float = 0.5
    hunt_success_hunger_restore: float = 2.0
    hunt_success_hp_restore: float = 0.2
    fight_damage_base: float = 1.0
    starvation_hp_damage: float = 1.0
