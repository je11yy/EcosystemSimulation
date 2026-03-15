from dataclasses import dataclass

from simulation_core.types import TerritoryId


@dataclass
class TerritoryState:
    """Состояние территории в мире симуляции.

    Содержит запасы еды, температуру и параметры регенерации.
    Территории являются узлами графа мира, где живут агенты.
    """

    id: TerritoryId  # Уникальный ID территории
    food: float  # Текущий запас еды
    temperature: float  # Температура территории

    food_regen_per_tick: float = 0.0  # Количество еды, регенерируемое за тик
    food_capacity: float = 0.0  # Максимальная вместимость еды

    def has_enough_food(self, amount: float = 1.0) -> bool:
        return self.food >= amount

    def consume_food(self, amount: float = 1.0) -> bool:
        if self.food < amount:
            return False
        self.food -= amount
        return True

    def regenerate_food(self) -> None:
        if self.food_regen_per_tick <= 0:
            return

        self.food = min(self.food + self.food_regen_per_tick, self.food_capacity)
