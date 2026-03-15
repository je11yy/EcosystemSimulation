from typing import Protocol, Sequence

from simulation_core.types import TerritoryId
from simulation_core.world.graph import TerritoryGraph
from simulation_core.world.territory import TerritoryState


class WorldReadAPI(Protocol):
    """Протокол для чтения состояния мира симуляции."""

    def get_territory(self, territory_id: TerritoryId) -> TerritoryState: ...

    def graph(self) -> TerritoryGraph: ...

    def all_territories(self) -> Sequence[TerritoryState]: ...
