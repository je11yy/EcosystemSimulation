from dataclasses import dataclass


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

    beta_default: float = 2.0  # "рациональность" для softmax/логит-выбора
