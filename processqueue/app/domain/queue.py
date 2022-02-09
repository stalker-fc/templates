import abc

from app.logger import get_logger

logger = get_logger(__name__)


__all__ = [
    "ITaskQueue"
]

class ITaskQueue(abc.ABC):

    @abc.abstractmethod
    async def put(self, task_id: int) -> None:
        pass

    @abc.abstractmethod
    async def get(self) -> int:
        pass

    @abc.abstractmethod
    async def cancel(self, task_id: int) -> None:
        pass

    @abc.abstractmethod
    async def is_task_cancelled(self, task_id: int) -> bool:
        pass
