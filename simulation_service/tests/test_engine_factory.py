import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulation_service.app.schemas.simulation.init import BuildSimulationRequest
from simulation_service.app.schemas.territory.edge import RuntimeTerritoryEdge
from simulation_service.app.schemas.territory.territory import RuntimeTerritory
from simulation_service.app.services.engine_factory import EngineFactory


class EngineFactoryTests(unittest.TestCase):
    def test_single_territory_edge_stays_directed_in_runtime(self) -> None:
        factory = EngineFactory()
        engine = factory.build(
            BuildSimulationRequest(
                simulation_id=1,
                territories=[
                    RuntimeTerritory(
                        id=1, food=10, temperature=20, food_regen_per_tick=1, food_capacity=10
                    ),
                    RuntimeTerritory(
                        id=2, food=10, temperature=20, food_regen_per_tick=1, food_capacity=10
                    ),
                ],
                territory_edges=[
                    RuntimeTerritoryEdge(source=1, target=2, weight=1.5),
                ],
            )
        )

        self.assertEqual(engine.world.get_neighbors(1), {2: 1.5})
        self.assertEqual(engine.world.get_neighbors(2), {})


if __name__ == "__main__":
    unittest.main()
