import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import List
from typing import Union

from app.domain.data import TaskStatus
from app.domain.repository import ITaskRepository
from app.domain.service import CancelTaskMessage
from app.domain.service import RunTaskMessage
from app.execution.executor import ExecutionConfig
from app.execution.handler import handle_task
from app.execution.storage import IExecutorTaskDataStorage
from app.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RunningTask:
    task_id: int
    task: asyncio.Task


@dataclass
class QueuedTask:
    task_id: int


class TaskMessageQueueListener:
    def __init__(
        self,
        task_message_queue: asyncio.Queue,
        task_repository: ITaskRepository,
        executor_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig,
        max_running_tasks: int
    ):
        self._task_message_queue = task_message_queue
        self._task_repository = task_repository
        self._executor_task_data_storage = executor_task_data_storage
        self._process_pool_executor = process_pool_executor
        self._execution_config = execution_config
        self._max_running_tasks = max_running_tasks

        self._running_tasks: List[RunningTask] = []
        self._queued_tasks: List[QueuedTask] = []


    async def listen(self):
        while True:
            message: Union[RunTaskMessage, CancelTaskMessage] = await self._task_message_queue.get()

            if isinstance(message, RunTaskMessage):
                await self._task_repository.set_task_status(message.task_id, TaskStatus.QUEUED)

                if len(self._running_tasks) < self._max_running_tasks:
                    await self._run(message.task_id)
                else:
                    self._queued_tasks.append(QueuedTask(message.task_id))

            elif isinstance(message, CancelTaskMessage):

                await self._task_repository.set_task_status(message.task_id, TaskStatus.CANCELLED)

            self._task_message_queue.task_done()

    async def _run(self, task_id: int):
        loop = asyncio.get_running_loop()
        task = loop.create_task(
            handle_task(
                self._task_repository,
                self._executor_task_data_storage,
                self._process_pool_executor,
                self._execution_config,
                task_id
            )
        )
        task.add_done_callback(self.__after_done_callback)
        running_task = RunningTask(
            task_id=task_id,
            task=task
        )
        self._running_tasks.append(running_task)

    def __after_done_callback(self, task: asyncio.Task):
        print("AHAHAHHAHAHAHAHHA")

