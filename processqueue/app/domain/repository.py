import abc

from app.domain.model import Task
from app.domain.model import TaskStatus
from app.domain.storage import IRepositoryTaskDataStorage
from app.domain.storage import InMemoryRepositoryTaskDataStorage
from app.exceptions import NoTaskOutputDataException
from app.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "build_task_repository",
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


class InMemoryTaskRepository(ITaskRepository):
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
        logger.info(f"task_id={task_id}. status={status.value}")
        task = await self._task_data_storage.get_task(task_id)
        task.status = status
        await self._task_data_storage.put_task(task)

    async def get_task_input_data(self, task_id: int) -> str:
        task = await self._task_data_storage.get_task(task_id)
        return task.input_data

    async def get_task_output_data(self, task_id: int) -> str:
        task = await self._task_data_storage.get_task(task_id)
        if task.output_data is None:
            raise NoTaskOutputDataException(task_id)

        return task.output_data


def build_task_repository() -> ITaskRepository:
    repository_task_data_storage = InMemoryRepositoryTaskDataStorage()
    return InMemoryTaskRepository(repository_task_data_storage)
