import abc
from typing import Dict

from app.domain.model import Task

__all__ = [
    "IRepositoryTaskDataStorage",
    "InMemoryRepositoryTaskDataStorage",
]

from app.exceptions import NoSuchTaskException


class IRepositoryTaskDataStorage(abc.ABC):
    @abc.abstractmethod
    async def get_task(self, task_id: int) -> Task:
        pass

    @abc.abstractmethod
    async def put_task(self, task: Task):
        pass


class InMemoryRepositoryTaskDataStorage(IRepositoryTaskDataStorage):
    def __init__(self):
        self._task_id_to_task: Dict[int, Task] = {}

    async def get_task(self, task_id: int) -> Task:
        try:
            return self._task_id_to_task[task_id]
        except KeyError:
            raise NoSuchTaskException(task_id)

    async def put_task(self, task: Task):
        self._task_id_to_task[task.task_id] = task
