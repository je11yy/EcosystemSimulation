from dataclasses import dataclass
from typing import Literal, Optional

from simulation_core.config import SimConfig
from simulation_core.types import IndividualId, TerritoryId
from simulation_core.utils import clamp


@dataclass
class IndividualState:
    """Состояние индивидуального агента в симуляции."""

    id: IndividualId  # Уникальный идентификатор агента
    location: TerritoryId  # ID территории, где находится агент

    # базовые характеристики
    base_strength: int  # 1..5 - сила агента (влияет на боевые действия)
    base_defense: int  # 1..5 - защита агента (сопротивление атакам)

    hunger: int  # 0..5 - уровень голода (0 = сыт, 5 = максимальный голод)
    hp: int  # 0..5 - здоровье (0 = мертв, 5 = полностью здоров)
    sex: Literal["male", "female"]  # Пол агента

    pregnant: bool = False  # Беременна ли самка
    ticks_to_birth: int = 0  # Тиков до рождения ребенка
    father_id: Optional[IndividualId] = None  # ID отца

    hunt_cooldown: int = 0

    base_temp_pref: float = 20.0  # Предпочитаемая температура
    satisfaction: float = 1.0  # Уровень удовлетворенности (для будущих механик)

    species_group: str = "default"  # Группа вида (для разных видов с разными шаблонами генома)

    alive: bool = True  # Жив ли агент

    def validate(self, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger, cfg.hunger_min, cfg.hunger_max)
        self.hp = clamp(self.hp, cfg.hp_min, cfg.hp_max)
        self.base_strength = clamp(self.base_strength, cfg.strength_min, cfg.strength_max)
        self.base_defense = clamp(self.base_defense, cfg.defense_min, cfg.defense_max)

    def increase_hunger(self, amount: int, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger + amount, cfg.hunger_min, cfg.hunger_max)

    def decrease_hunger(self, amount: int, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger - amount, cfg.hunger_min, cfg.hunger_max)

    def decrease_hp(self, amount: int, cfg: SimConfig) -> None:
        self.hp = clamp(self.hp - amount, cfg.hp_min, cfg.hp_max)
        if self.hp <= cfg.hp_min:
            self.alive = False

    def move_to(self, territory_id: TerritoryId) -> None:
        self.location = territory_id
