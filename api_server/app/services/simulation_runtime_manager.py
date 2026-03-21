from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RunningSimulationHandle:
    simulation_id: int
    task: asyncio.Task[None]
    lock: asyncio.Lock


class SimulationRuntimeManager:
    def __init__(self) -> None:
        self._running: Dict[int, RunningSimulationHandle] = {}
        self._global_lock = asyncio.Lock()

    def is_running(self, simulation_id: int) -> bool:
        handle = self._running.get(simulation_id)
        return handle is not None and not handle.task.done()

    def get_lock(self, simulation_id: int) -> asyncio.Lock:
        handle = self._running.get(simulation_id)
        if handle is not None:
            return handle.lock
        return asyncio.Lock()

    async def start_loop(
        self,
        simulation_id: int,
        coro_factory: Callable[[], Coroutine[Any, Any, None]],
    ) -> bool:
        """
        coro_factory: async callable без аргументов, возвращает coroutine loop-а
        """
        async with self._global_lock:
            if self.is_running(simulation_id):
                return False

            lock = asyncio.Lock()
            task = asyncio.create_task(coro_factory())
            self._running[simulation_id] = RunningSimulationHandle(
                simulation_id=simulation_id,
                task=task,
                lock=lock,
            )
            return True

    async def stop_loop(self, simulation_id: int) -> bool:
        async with self._global_lock:
            handle = self._running.get(simulation_id)
            if handle is None:
                return False
            handle.task.cancel()
            self._running.pop(simulation_id, None)

        try:
            await handle.task
        except asyncio.CancelledError:
            pass

        return True

    async def cleanup_finished(self, simulation_id: int) -> None:
        async with self._global_lock:
            handle = self._running.get(simulation_id)
            if handle is not None and handle.task.done():
                self._running.pop(simulation_id, None)

    async def stop_all(self) -> None:
        ids = list(self._running.keys())
        for simulation_id in ids:
            await self.stop_loop(simulation_id)
