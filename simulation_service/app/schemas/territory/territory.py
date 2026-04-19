from pydantic import BaseModel


class RuntimeTerritory(BaseModel):
    id: int
    food: float = 0.0
    temperature: float = 20.0
    food_regen_per_tick: float = 0.0
    food_capacity: float = 0.0
