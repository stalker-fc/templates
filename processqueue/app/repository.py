import abc
from typing import Optional

from app.model import TaskStatus, Task
from app.storage import IRepositoryTaskDataStorage


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


class DummyTaskRepository(ITaskRepository):
    def __init__(self, task_data_storage: IRepositoryTaskDataStorage):
        self._counter = 0
        self._task_data_storage = task_data_storage

    async def create_task(self, input_data: str) -> Task:
        task = Task(
            task_id=self._counter,
            status=TaskStatus.CREATED,
            input_data=input_data,
            output_data=None
        )
        await self._task_data_storage.put_task(task)
        self._counter += 1
        return task

    async def get_task(self, task_id: int) -> Task:
        return await self._task_data_storage.get_task(task_id)

    async def add_task_output_data(self, task_id: int, output_data: str) -> None:
        task = await self._task_data_storage.get_task(task_id)
        task.output_data = output_data
        await self._task_data_storage.put_task(task)

    async def get_task_status(self, task_id: int) -> TaskStatus:
        task = await self._task_data_storage.get_task(task_id)
        return task.status

    async def set_task_status(self, task_id: int, status: TaskStatus) -> None:
        task = await self._task_data_storage.get_task(task_id)
        task.status = status
        await self._task_data_storage.put_task(task)

    async def get_task_input_data(self, task_id: int) -> str:
        task = await self._task_data_storage.get_task(task_id)
        return task.input_data

    async def get_task_output_data(self, task_id: int) -> Optional[str]:
        task = await self._task_data_storage.get_task(task_id)
        return task.output_data