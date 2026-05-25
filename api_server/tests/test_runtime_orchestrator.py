import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.services.simulation.runtime_orchestrator import SimulationRuntimeOrchestrator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.pop("app", None)


class SimulationRuntimeOrchestratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_batch_persists_each_tick_and_applies_final_snapshot(self) -> None:
        session = SimpleNamespace(commit=AsyncMock())
        orchestrator = SimulationRuntimeOrchestrator(session)
        simulation = SimpleNamespace(tick=0, status="draft")

        orchestrator._build_payload_or_404 = AsyncMock(
            return_value=(simulation, {"simulation_id": 11})
        )
        orchestrator.runtime = SimpleNamespace(
            run_batch=AsyncMock(
                return_value={
                    "tick_results": [
                        {
                            "result": {
                                "tick": 0,
                                "births": [{"child_id": 101, "parent_id": 1, "partner_id": 2}],
                            },
                            "snapshot": {"tick": 1, "simulation_id": 11},
                        },
                        {
                            "result": {"tick": 1, "births": []},
                            "snapshot": {"tick": 2, "simulation_id": 11},
                        },
                    ],
                    "final_snapshot": {"tick": 2, "simulation_id": 11},
                }
            )
        )
        orchestrator.persister = SimpleNamespace(
            save_result=AsyncMock(),
            apply_snapshot=AsyncMock(),
        )

        await orchestrator.run_batch(user_id=5, simulation_id=11, steps=2)

        self.assertEqual(orchestrator.persister.save_result.await_count, 2)
        orchestrator.persister.save_result.assert_any_await(
            11,
            {"tick": 0, "births": [{"child_id": 101, "parent_id": 1, "partner_id": 2}]},
            {"tick": 1, "simulation_id": 11},
        )
        orchestrator.persister.save_result.assert_any_await(
            11,
            {"tick": 1, "births": []},
            {"tick": 2, "simulation_id": 11},
        )
        orchestrator.persister.apply_snapshot.assert_awaited_once_with(
            5,
            {"tick": 2, "simulation_id": 11},
            {"births": [{"child_id": 101, "parent_id": 1, "partner_id": 2}]},
        )
        session.commit.assert_awaited_once()
        self.assertEqual(simulation.tick, 2)
        self.assertEqual(simulation.status, "stopped")


if __name__ == "__main__":
    unittest.main()
