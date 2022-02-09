import abc

from app.domain.model import Task
from app.domain.model import TaskStatus


__all__ = [
    "ITaskRepository"
]


class ITaskRepository(abc.ABC):

    @abc.abstractmethod
    async def create_task(self, input_data: str) -> Task:
        pass

    @abc.abstractmethod
    async def get_task(self, task_id: int) -> Task:
        pass

    @abc.abstractmethod
    async def add_task_output_data(self, task_id: int, output_data: str) -> None:
        pass

    @abc.abstractmethod
    async def get_task_status(self, task_id: int) -> TaskStatus:
        pass

    @abc.abstractmethod
    async def set_task_status(self, task_id: int, status: TaskStatus) -> None:
        pass

    @abc.abstractmethod
    async def get_task_input_data(self, task_id: int) -> str:
        pass

    @abc.abstractmethod
    async def get_task_output_data(self, task_id: int) -> str:
        pass
