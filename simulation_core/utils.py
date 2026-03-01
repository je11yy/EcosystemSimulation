from types import IndividualId, TerritoryId

from agents.state import IndividualState


# ограниченное целое
def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


# создание особи
def create_individual(
    id: str, location: str, hunger: int, strength: int, defense: int
) -> IndividualState:
    return IndividualState(
        id=IndividualId(id),
        location=TerritoryId(location),
        hunger=hunger,
        strength=strength,
        defense=defense,
    )
