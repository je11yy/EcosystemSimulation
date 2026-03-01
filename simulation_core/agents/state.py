from dataclasses import dataclass

from simulation_core.config import SimConfig
from simulation_core.types import IndividualId, TerritoryId
from simulation_core.utils import clamp


@dataclass
class IndividualState:
    id: IndividualId
    location: TerritoryId

    hunger: int
    strength: int
    defense: int

    pregnant: bool = False
    ticks_to_birth: int = 0

    temp_pref: float = 20.0
    satisfaction: float = 1.0

    def validate(self, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger, cfg.hunger_min, cfg.hunger_max)
        self.strength = clamp(self.strength, cfg.strength_min, cfg.strength_max)
        self.defense = clamp(self.defense, cfg.defense_min, cfg.defense_max)

    def increase_hunger(self, amount: int, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger + amount, cfg.hunger_min, cfg.hunger_max)

    def decrease_hunger(self, amount: int, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger - amount, cfg.hunger_min, cfg.hunger_max)

    def is_starving(self, cfg: SimConfig) -> bool:
        return self.hunger >= cfg.hunger_max

    def is_full(self, cfg: SimConfig) -> bool:
        return self.hunger <= cfg.hunger_min

    def is_pregnant(self) -> bool:
        return self.pregnant

    def start_pregnancy(self, gestation_period: int) -> None:
        self.pregnant = True
        self.ticks_to_birth = gestation_period

    def progress_pregnancy(self) -> None:
        if self.pregnant:
            self.ticks_to_birth -= 1
            if self.ticks_to_birth <= 0:
                self.pregnant = False
                self.ticks_to_birth = 0

    def can_give_birth(self) -> bool:
        return self.pregnant and self.ticks_to_birth == 0

    def give_birth(self) -> None:
        if self.can_give_birth():
            self.pregnant = False
            self.ticks_to_birth = 0
