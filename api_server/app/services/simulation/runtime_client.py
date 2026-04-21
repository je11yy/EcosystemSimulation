from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


class SimulationRuntimeClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.simulation_service_base_url).rstrip("/")

    async def build(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/runtime/build", payload)

    async def step(self, simulation_id: int) -> dict[str, Any]:
        return await self._post(f"/runtime/{simulation_id}/step", {})

    async def start(
        self,
        simulation_id: int,
        interval_seconds: float | None = None,
        max_steps: int | None = None,
    ) -> dict[str, Any]:
        payload = {
            "interval_seconds": interval_seconds,
            "max_steps": max_steps,
        }
        return await self._post(f"/runtime/{simulation_id}/start", payload)

    async def pause(self, simulation_id: int) -> dict[str, Any]:
        return await self._post(f"/runtime/{simulation_id}/pause", {})

    async def drain(self, simulation_id: int) -> dict[str, Any]:
        return await self._post(f"/runtime/{simulation_id}/drain", {})

    async def stop(self, simulation_id: int) -> dict[str, Any]:
        return await self._post(f"/runtime/{simulation_id}/stop", {})

    async def state(self, simulation_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.get(f"/runtime/{simulation_id}/state")
        return self._handle_response(response)

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
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
