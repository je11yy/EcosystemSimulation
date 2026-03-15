from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.genome.state import GenomeState
from simulation_core.types import TerritoryId
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class GenomeContext:
    """Внешний контекст для обновления состояния генома.

    Содержит информацию об окружении агента, которая может влиять
    на активацию генов. В будущем можно расширить для включения
    температуры, голода, беременности, повреждений и т.д.
    """

    territory_id: TerritoryId  # ID территории, где находится агент


@runtime_checkable
class GenomeUpdater(Protocol):
    """Протокол для обновления состояния генома агента.

    Определяет интерфейс компонента, который на основе генома,
    текущего состояния и внешнего контекста вычисляет новое
    состояние активности генов.
    """

    def next_state(
        self,
        genome: Genome,  # Геном агента
        current_state: GenomeState,  # Текущее состояние генома
        context: GenomeContext,  # Внешний контекст
        world: WorldReadAPI,  # Доступ к миру
    ) -> GenomeState:
        """Вычисляет следующее состояние генома."""
        ...
