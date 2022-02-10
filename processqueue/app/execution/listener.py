import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import List

from app.domain.listener import ITaskQueueListener
from app.domain.model import TaskStatus
from app.domain.queue import ITaskQueue
from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.handler import TaskExecutionProcess
from app.execution.handler import handle_cpu_bound_task
from app.execution.handler import handle_long_cpu_bound_task
from app.execution.storage import build_executor_task_data_storage
from app.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "build_task_queue_listener",
    "ListenerConfig"
]

@dataclass
class ListenerConfig:
    execution_config: ExecutionConfig
    max_running_tasks: int = 1


class RunningTasksObserver:
    def __init__(self, max_running_tasks: int):
        self._max_running_tasks = max_running_tasks
        self._current_running_tasks = 0

    def has_available_slot(self) -> bool:
        return self._current_running_tasks < self._max_running_tasks

    def take_slot(self):
        self._current_running_tasks += 1

    def return_slot(self):
        self._current_running_tasks -= 1


class TaskQueueListener(ITaskQueueListener):
    def __init__(self, task_repository: ITaskRepository, task_queue: ITaskQueue, config: ListenerConfig):
        self._task_repository = task_repository
        self._task_queue = task_queue
        self._config = config
        self._process_pool_executor = ProcessPoolExecutor(max_workers=self._config.max_running_tasks)
        self._loop = asyncio.get_running_loop()
        self._running_tasks_observer = RunningTasksObserver(self._config.max_running_tasks)
        self._executor_task_data_storage = build_executor_task_data_storage(
            self._config.execution_config.executor_task_data_storage_config
        )

    async def listen(self):
        while True:
            if self._running_tasks_observer.has_available_slot():
                task_id: int = await self._task_queue.get()
                logger.info(f"Received task id=`{task_id}`.")

                is_task_cancelled = await self._task_queue.is_task_cancelled(task_id)
                if is_task_cancelled:
                    continue

                self._running_tasks_observer.take_slot()
                running_task = self._loop.create_task(
                    handle_cpu_bound_task(
                        self._task_repository,
                        self._executor_task_data_storage,
                        self._process_pool_executor,
                        self._config.execution_config,
                        task_id
                    )
                )
                running_task.add_done_callback(lambda _: self._running_tasks_observer.return_slot())

            else:
                await asyncio.sleep(2.)

    def stop(self):
        self._process_pool_executor.shutdown(wait=True)


class LongTaskQueueListener(ITaskQueueListener):
    def __init__(self, task_repository: ITaskRepository, task_queue: ITaskQueue, config: ListenerConfig):
        self._task_repository = task_repository
        self._task_queue = task_queue
        self._config = config
        self._executor_task_data_storage = build_executor_task_data_storage(
            self._config.execution_config.executor_task_data_storage_config
        )
        self._running_tasks_observer = RunningTasksObserver(self._config.max_running_tasks)
        self._running_tasks: List[TaskExecutionProcess] = []

    def listen(self):
        while True:
            if len(self._running_tasks) < self._config.max_running_tasks \
                    and not self._task_queue.is_empty():
                task_id: int = await self._task_queue.get()
                logger.info(f"Received task id=`{task_id}`.")

                is_task_cancelled = await self._task_queue.is_task_cancelled(task_id)
                if is_task_cancelled:
                    continue

                self._running_tasks_observer.take_slot()
                running_task = await handle_long_cpu_bound_task(
                    self._task_repository,
                    self._executor_task_data_storage,
                    self._config.execution_config,
                    task_id
                )
                self._running_tasks.append(running_task)

            still_running_tasks = []
            for task in self._running_tasks:
                if task.process.is_alive():
                    still_running_tasks.append(task)
                else:
                    if task.process.exitcode == 0:
                        logger.info(f"Execution of task id=`{task.task_id}` is completed successfully.")
                        await self._task_repository.set_task_status(task.task_id, TaskStatus.SUCCESS)
                        output_data = self._executor_task_data_storage.get_output_data(task.task_id)
                        await self._task_repository.add_task_output_data(task.task_id, output_data)
                    else:
                        logger.info(f"Execution of task id=`{task.task_id}` is failed.")
                        await self._task_repository.set_task_status(task.task_id, TaskStatus.FAILURE)

            self._running_tasks = still_running_tasks
            asyncio.sleep(2.0)

    def stop(self):
        for task in self._running_tasks:
            if task.process.is_alive():
                task.process.join()



def build_task_queue_listener(
    task_repository: ITaskRepository,
    task_queue: ITaskQueue,
    config: ListenerConfig
) -> ITaskQueueListener:
    return TaskQueueListener(
        task_repository,
        task_queue,
        config
    )
