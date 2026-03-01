from typing import Protocol

from simulation_core.types import TerritoryId
from simulation_core.world.graph import TerritoryGraph
from simulation_core.world.territory import TerritoryState


class WorldReadAPI(Protocol):
    def get_territory(self, territory_id: TerritoryId) -> TerritoryState: ...

    def graph(self) -> TerritoryGraph: ...
