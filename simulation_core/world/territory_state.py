from dataclasses import dataclass


@dataclass
class TerritoryState:
    id: int
    food: float
    temperature: float

    food_regen_per_tick: float
    food_capacity: float

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.food_capacity = max(0, self.food_capacity)
        self.food_regen_per_tick = max(0, self.food_regen_per_tick)
        self.food = min(self.food_capacity, max(0, self.food))

    def has_enough_food(self, amount: float) -> bool:
        return self.food >= amount

    def consume_food(self, amount: float) -> None:
        self.food = max(0, self.food - amount)

    def regenerate_food(self) -> None:
        self.food = min(self.food_capacity, self.food + self.food_regen_per_tick)
