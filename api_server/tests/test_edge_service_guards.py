import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from fastapi import HTTPException

from app.schemas.base import Position
from app.schemas.genome.edge import GeneEdgeCreate
from app.schemas.genome.gene import GeneCreate
from app.schemas.territory.territory import TerritoryEdgeCreate
from app.services.genome.service import GenomeService
from app.services.territory.service import TerritoryService

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.modules.pop("app", None)


class EdgeServiceGuardsTests(unittest.IsolatedAsyncioTestCase):
    async def test_territory_service_rejects_duplicate_directed_edge(self) -> None:
        session = SimpleNamespace(
            get=AsyncMock(return_value=object()),
            scalar=AsyncMock(return_value=object()),
            add=Mock(),
            commit=AsyncMock(),
        )
        service = TerritoryService(session)
        service.territories = SimpleNamespace(
            simulation_id_for_territory=AsyncMock(side_effect=[5, 5])
        )
        service._ensure_simulation_owned = AsyncMock()
        service.runtime_orchestrator = SimpleNamespace(mark_runtime_stale=AsyncMock())

        with self.assertRaises(HTTPException) as error:
            await service.create_edge(
                TerritoryEdgeCreate(source=1, target=2, weight=3.0),
                user_id=9,
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Edge already exists")
        service.runtime_orchestrator.mark_runtime_stale.assert_not_awaited()
        session.add.assert_not_called()
        session.commit.assert_not_awaited()

    async def test_territory_service_allows_reverse_edge_with_distinct_direction(self) -> None:
        session = SimpleNamespace(
            get=AsyncMock(return_value=object()),
            scalar=AsyncMock(return_value=None),
            add=Mock(),
            commit=AsyncMock(),
        )
        service = TerritoryService(session)
        service.territories = SimpleNamespace(
            simulation_id_for_territory=AsyncMock(side_effect=[5, 5])
        )
        service._ensure_simulation_owned = AsyncMock()
        service.runtime_orchestrator = SimpleNamespace(mark_runtime_stale=AsyncMock())

        await service.create_edge(
            TerritoryEdgeCreate(source=7, target=3, weight=2.5),
            user_id=9,
        )

        added_edge = session.add.call_args.args[0]
        self.assertEqual(added_edge.source_id, 7)
        self.assertEqual(added_edge.target_id, 3)
        self.assertEqual(added_edge.movement_cost, 2.5)
        service.runtime_orchestrator.mark_runtime_stale.assert_awaited_once_with(9, 5)
        session.commit.assert_awaited_once()

    async def test_genome_service_rejects_duplicate_directed_edge(self) -> None:
        session = SimpleNamespace(
            scalar=AsyncMock(return_value=object()),
            add=Mock(),
            commit=AsyncMock(),
        )
        service = GenomeService(session)
        service.genomes = SimpleNamespace(
            get_owned=AsyncMock(
                return_value=SimpleNamespace(
                    gene_links=[
                        SimpleNamespace(gene_id=10),
                        SimpleNamespace(gene_id=11),
                    ]
                )
            )
        )
        service._mark_related_simulations_stale = AsyncMock()

        with self.assertRaises(HTTPException) as error:
            await service.create_edge(
                genome_id=4,
                user_id=7,
                payload=GeneEdgeCreate(source=10, target=11, weight=1.5),
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Edge already exists")
        service._mark_related_simulations_stale.assert_not_awaited()
        session.add.assert_not_called()
        session.commit.assert_not_awaited()

    async def test_genome_service_rejects_duplicate_effect_type(self) -> None:
        session = SimpleNamespace(add=Mock(), commit=AsyncMock(), flush=AsyncMock())
        service = GenomeService(session)
        service.genomes = SimpleNamespace(
            get_owned=AsyncMock(
                return_value=SimpleNamespace(
                    gene_links=[
                        SimpleNamespace(
                            gene=SimpleNamespace(id=1, effect_type="MAX_HP"),
                            gene_id=1,
                        )
                    ]
                )
            )
        )
        service.runtime_orchestrator = SimpleNamespace(mark_runtime_stale=AsyncMock())

        with self.assertRaises(HTTPException) as error:
            await service.create_gene(
                genome_id=4,
                user_id=7,
                payload=GeneCreate(
                    effect_type="MAX_HP",
                    threshold=1.0,
                    weight=1.2,
                    position=Position(x=100, y=100),
                    default_active=True,
                ),
            )

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail,
            "Gene with this effect type already exists in genome",
        )
        service.runtime_orchestrator.mark_runtime_stale.assert_not_awaited()
        session.add.assert_not_called()
        session.flush.assert_not_awaited()
        session.commit.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
