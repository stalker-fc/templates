import abc

from app.domain.queue import ITaskQueue
from app.domain.repository import ITaskRepository


class ITaskQueueListener(abc.ABC):
    @abc.abstractmethod
    def __init__(self, task_repository: ITaskRepository, task_queue: ITaskQueue):
        self._task_repository = task_repository
        self._task_queue = task_queue

    @abc.abstractmethod
    async def listen(self):
        pass
