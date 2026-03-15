from dataclasses import asdict, dataclass
from typing import Sequence

from simulation_core.dto.agent_dto import AgentDTO
from simulation_core.dto.territory_dto import TerritoryDTO


@dataclass(frozen=True)
class SimulationStateDTO:
    """DTO для полного состояния симуляции на определенный момент времени.

    Содержит текущее состояние всех территорий и агентов,
    а также номер тика симуляции.
    """

    tick: int  # Номер текущего тика симуляции
    territories: Sequence[TerritoryDTO]  # Список всех территорий с их состоянием
    agents: Sequence[AgentDTO]  # Список всех агентов с их состоянием

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
