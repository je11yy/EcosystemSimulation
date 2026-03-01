from dataclasses import dataclass
from typing import Dict

from simulation_core.types import TerritoryId
from simulation_core.world.api import WorldReadAPI
from simulation_core.world.graph import TerritoryGraph
from simulation_core.world.territory import TerritoryState


@dataclass
class WorldState(WorldReadAPI):
    territories: Dict[TerritoryId, TerritoryState]
    _graph: TerritoryGraph

    def get_territory(self, territory_id: TerritoryId) -> TerritoryState:
        return self.territories[territory_id]

    def graph(self) -> TerritoryGraph:
        return self._graph
