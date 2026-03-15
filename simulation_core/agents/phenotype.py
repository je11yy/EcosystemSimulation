from dataclasses import dataclass


@dataclass(frozen=True)
class PhenotypeSnapshot:
    """
    Актуальные (effective) характеристики агента на текущем тике.
    """

    strength: int
    defense: int
    temp_pref: float
