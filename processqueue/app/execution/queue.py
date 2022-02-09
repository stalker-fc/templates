import asyncio
from typing import Set

from app.domain.queue import ITaskQueue
from app.logger import get_logger

__all__ = [
    "build_task_queue"
]

logger = get_logger(__name__)


class TaskQueue(ITaskQueue):
    def __init__(self):
        self._queue = asyncio.Queue()
        self._cancelled_tasks: Set[int] = set()

    async def put(self, task_id: int) -> None:
        if task_id in self._cancelled_tasks:
            self._cancelled_tasks.remove(task_id)
        await self._queue.put(task_id)

    async def get(self) -> int:
        task_id: int = await self._queue.get()
        self._queue.task_done()
        return task_id

    async def cancel(self, task_id: int) -> None:
        self._cancelled_tasks.add(task_id)

    async def is_task_cancelled(self, task_id: int) -> bool:
        return task_id in self._cancelled_tasks

    async def is_empty(self) -> bool:
        return self._queue.empty()



def build_task_queue() -> ITaskQueue:
    return TaskQueue()
