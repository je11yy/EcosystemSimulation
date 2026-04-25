from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


class SimulationRuntimeClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.simulation_service_base_url).rstrip("/")

    async def run_batch(self, payload: dict[str, Any], steps: int) -> dict[str, Any]:
        return await self._post(
            "/runtime/run-batch",
            {
                "build": payload,
                "steps": steps,
            },
            timeout=120.0,
        )

    async def _post(
        self,
        path: str,
        payload: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
            response = await client.post(path, json=payload)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            detail: Any = response.text
            try:
                detail = response.json()
            except ValueError:
                pass
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Simulation service request failed",
                    "status_code": response.status_code,
                    "response": detail,
                },
            )
        return response.json()
