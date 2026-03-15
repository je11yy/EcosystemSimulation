from typing import Protocol, runtime_checkable

from simulation_core.world.api import WorldReadAPI


@runtime_checkable
class FoodDiffusionModel(Protocol):
    def diffuse(self, world: WorldReadAPI) -> None: ...
