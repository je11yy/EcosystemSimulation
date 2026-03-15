from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.genome.state import GenomeState


@dataclass(frozen=True)
class GenomeEffects:
    """Эффекты активных генов на характеристики агента.

    Определяет, как активные гены модифицируют базовые параметры агента.
    В будущем можно добавить utility-веса, риск, фертильность и т.д.
    """

    strength_delta: int = 0  # Изменение силы (+ увеличивает, - уменьшает)
    defense_delta: int = 0  # Изменение защиты (+ увеличивает, - уменьшает)
    temp_pref_delta: float = 0.0  # Изменение предпочтительной температуры (+ теплее, - холоднее)


@runtime_checkable
class GenomeEffectsResolver(Protocol):
    # Протокол для вычисления эффектов генома на агента.

    def resolve(
        self,
        genome: Genome,  # Геном агента
        genome_state: GenomeState,  # Состояние генома
    ) -> GenomeEffects:
        # Вычисляет эффекты активных генов.
        ...
