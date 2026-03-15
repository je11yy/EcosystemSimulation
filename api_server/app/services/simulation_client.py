from typing import Any

import httpx

from app.core.config import settings
from app.schemas.simulation_runtime import SimulationInitDTO


class SimulationClient:
    def __init__(self) -> None:
        self.base_url = settings.simulation_service_base_url

    async def healthcheck(self) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()

    async def init_runtime(self, payload: SimulationInitDTO) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            response = await client.post(
                "/runtime/start",
                json=payload.model_dump(),
            )
            response.raise_for_status()
            return response.json()
