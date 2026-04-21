from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SimConfig:
    # Голод
    hunger_min: int = 0
    hunger_max: int = 5

    # Сила
    strength_min: int = 1
    strength_max: int = 5

    # Защита
    defense_min: int = 1
    defense_max: int = 5

    # Здоровье
    hp_min: int = 0
    hp_max: int = 5

    # Удовлетворенность агента: интегральная оценка текущего места и состояния.
    # Используется генами и политикой решений.
    satisfaction_min: float = 0.0
    satisfaction_max: float = 5.0

    beta_default: float = 2.0
    random_seed: Optional[int] = None

    pregnancy_duration_ticks: int = 3
    hunt_cooldown_ticks: int = 2
    mate_reconsider_hunger_threshold: float = 0.8
    mate_reconsider_score_margin: float = 0.15
    newborn_hp: float = 3.0
    newborn_hunger: float = 1.0
    newborn_satisfaction: float = 3.0
    # Затраты на действия, похожие на DEB-модель. Голод используется как прокси
    # текущего энергетического дефицита:
    # чем выше голод, тем меньше доступной энергии у агента.
    maintenance_hunger_cost: float = 0.1
    eat_hunger_cost: float = 0.2
    move_hunger_cost: float = 0.5
    mate_hunger_cost: float = 1.0
    rest_hunger_cost: float = 0.05
    hunt_hunger_cost: float = 0.9

    # Если стоимость действия превышает доступный запас голода,
    # переполнение приводит к потере здоровья.
    hunger_overflow_hp_damage_factor: float = 1.0

    # Генетические признаки уменьшают связанные затраты на действия, но никогда не ниже этой доли.
    min_trait_cost_multiplier: float = 0.25

    food_per_eat: float = 1.0
    eat_hunger_restore: float = 1.5
    rest_hp_recovery: float = 0.2

    hunt_base_damage: float = 0.8
    hunt_counter_damage: float = 0.7
    hunt_success_hunger_restore: float = 1.6
    hunt_success_hp_restore: float = 0.1
    defend_hunger_cost: float = 0.15
    hunt_defense_reaction_multiplier: float = 1.22

    fight_damage_base: float = 1.0
    starvation_hp_damage: float = 1.0
