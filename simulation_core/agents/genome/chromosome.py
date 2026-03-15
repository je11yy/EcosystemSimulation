from dataclasses import dataclass
from typing import Sequence

from simulation_core.agents.genome.gene import Gene


@dataclass(frozen=True)
class ChromosomeView:
    chromosome_id: str
    genes: Sequence[Gene]
