from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
    # Голод
    hunger_min: int = 0  # Минимальный уровень голода (агент сыт)
    hunger_max: int = 5  # Максимальный уровень голода (агент умирает)

    # Сила
    strength_min: int = 1  # Минимальная сила агента
    strength_max: int = 5  # Максимальная сила агента

    # Защита
    defense_min: int = 1  # Минимальная защита агента
    defense_max: int = 5  # Максимальная защита агента

    # Здоровье
    hp_min: int = 0
    hp_max: int = 5

    beta_default: float = 2.0  # "рациональность" для softmax/логит-выбора

    pregnancy_duration_ticks: int = 3  # Длительность беременности в тиках
