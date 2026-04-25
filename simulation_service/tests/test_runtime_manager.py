import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulation_service.app.schemas.agent import RuntimeAgent
from simulation_service.app.schemas.simulation.batch import RunBatchSimulationRequest
from simulation_service.app.schemas.simulation.init import BuildSimulationRequest
from simulation_service.app.schemas.territory.territory import RuntimeTerritory
from simulation_service.app.services.runtime_manager import RuntimeManager


class RuntimeManagerBatchRunTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_batch_returns_snapshot_for_each_tick(self) -> None:
        manager = RuntimeManager()
        payload = RunBatchSimulationRequest(
            build=BuildSimulationRequest(
                simulation_id=7,
                territories=[
                    RuntimeTerritory(
                        id=1,
                        food=8.0,
                        temperature=20.0,
                        food_regen_per_tick=1.0,
                        food_capacity=12.0,
                    )
                ],
                agents=[
                    RuntimeAgent(
                        id=1,
                        sex="female",
                        territory_id=1,
                        hunger=2.0,
                        hp=5.0,
                    )
                ],
            ),
            steps=3,
        )

        response = await manager.run_batch(payload)

        self.assertEqual(response.simulation_id, 7)
        self.assertEqual(response.steps, 3)
        self.assertEqual(len(response.tick_results), 3)
        self.assertEqual([tick.result["tick"] for tick in response.tick_results], [0, 1, 2])
        self.assertEqual([tick.snapshot.tick for tick in response.tick_results], [1, 2, 3])
        self.assertEqual(response.final_snapshot.tick, 3)
        self.assertTrue(all(tick.snapshot.agents for tick in response.tick_results))
        self.assertTrue(all(tick.snapshot.territories for tick in response.tick_results))


if __name__ == "__main__":
    unittest.main()
