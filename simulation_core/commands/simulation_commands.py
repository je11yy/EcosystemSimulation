from dataclasses import dataclass

from simulation_core.types import TerritoryId


@dataclass(frozen=True)
class StepCommand:
    steps: int = 1  # Количество шагов для выполнения (по умолчанию 1)


@dataclass(frozen=True)
class SetTerritoryFoodCommand:
    territory_id: TerritoryId  # ID территории для изменения
    food: float  # Новое количество еды на территории


@dataclass(frozen=True)
class SetTerritoryTemperatureCommand:
    territory_id: TerritoryId  # ID территории для изменения
    temperature: float  # Новая температура на территории
