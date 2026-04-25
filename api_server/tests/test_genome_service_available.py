import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.services.genome.service import GenomeService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.pop("app", None)


class GenomeServiceAvailableTests(unittest.IsolatedAsyncioTestCase):
    async def test_available_for_user_does_not_touch_lazy_user_links(self) -> None:
        session = SimpleNamespace(commit=AsyncMock())
        service = GenomeService(session)
        service.genomes = SimpleNamespace(
            available_for_user=AsyncMock(
                return_value=[
                    SimpleNamespace(
                        id=1,
                        name="Базовый травоядный",
                        is_template=True,
                    )
                ]
            )
        )

        with patch("app.services.genome.service.ScenarioService") as scenario_service:
            scenario_service.return_value.ensure_template_genomes = AsyncMock()

            result = await service.available_for_user(42)

        self.assertEqual(
            result,
            [
                {
                    "id": 1,
                    "name": "Базовый травоядный",
                    "is_template": True,
                    "template_key": "balanced_grazer",
                }
            ],
        )
        scenario_service.return_value.ensure_template_genomes.assert_awaited_once()
        session.commit.assert_awaited_once()
        service.genomes.available_for_user.assert_awaited_once_with(42)


if __name__ == "__main__":
    unittest.main()
