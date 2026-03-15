from dataclasses import dataclass
from typing import Dict, Sequence

from simulation_core.types import TerritoryId
from simulation_core.world.api import WorldReadAPI
from simulation_core.world.graph import TerritoryGraph
from simulation_core.world.territory import TerritoryState


@dataclass
class WorldState(WorldReadAPI):
    """Реализация состояния мира симуляции.

    Хранит все территории и их связи, предоставляет интерфейс
    для чтения и модификации состояния мира.
    """

    territories: Dict[TerritoryId, TerritoryState]  # Словарь территорий по ID
    _graph: TerritoryGraph  # Граф связей между территориями

    def get_territory(self, territory_id: TerritoryId) -> TerritoryState:
        return self.territories[territory_id]

    def graph(self) -> TerritoryGraph:
        return self._graph

    def all_territories(self) -> Sequence[TerritoryState]:
        return list(self.territories.values())

    def set_territory_food(self, territory_id: TerritoryId, food: float) -> None:
        self.territories[territory_id].food = food

    def set_territory_temperature(self, territory_id: TerritoryId, temperature: float) -> None:
        self.territories[territory_id].temperature = temperature
