from agents.state import IndividualId, IndividualState, TerritoryId


# ограниченное целое
def clamp(value: int, min_value: int, max_value: int) -> int:
    """Ограничивает значение в заданных пределах."""
    return max(min_value, min(value, max_value))


# создание особи
def create_individual(
    id: str, location: str, hunger: int, strength: int, defense: int, sex: str
) -> IndividualState:
    if sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")
    return IndividualState(
        id=IndividualId(id),
        location=TerritoryId(location),
        hunger=hunger,
        base_strength=strength,
        base_defense=defense,
        sex=sex,  # type: ignore
    )
