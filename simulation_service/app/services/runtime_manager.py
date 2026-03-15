from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict

from simulation_core.engine.engine import SimulationEngine


@dataclass
class RuntimeHandle:
    simulation_id: str
    engine: SimulationEngine
    lock: asyncio.Lock


class RuntimeManager:
    def __init__(self) -> None:
        self._runtimes: Dict[str, RuntimeHandle] = {}

    def has(self, simulation_id: str) -> bool:
        return simulation_id in self._runtimes

    def get(self, simulation_id: str) -> RuntimeHandle:
        return self._runtimes[simulation_id]

    def put(self, simulation_id: str, engine: SimulationEngine) -> RuntimeHandle:
        handle = RuntimeHandle(
            simulation_id=simulation_id,
            engine=engine,
            lock=asyncio.Lock(),
        )
        self._runtimes[simulation_id] = handle
        return handle

    def delete(self, simulation_id: str) -> bool:
        return self._runtimes.pop(simulation_id, None) is not None

    def list_ids(self) -> list[str]:
        return list(self._runtimes.keys())
