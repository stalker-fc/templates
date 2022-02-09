import asyncio
from concurrent.futures import ProcessPoolExecutor

from app.domain.queue import ITaskQueue
from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.handler import handle_cpu_bound_task
from app.execution.storage import IExecutorTaskDataStorage
from app.logger import get_logger

logger = get_logger(__name__)


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


async def task_queue_listener(
        task_queue: ITaskQueue,
        task_repository: ITaskRepository,
        executor_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig,
        max_running_tasks: int
) -> None:
    loop = asyncio.get_running_loop()
    running_tasks_observer = RunningTasksObserver(max_running_tasks)
    while True:
        if running_tasks_observer.has_available_slot():
            task_id: int = await task_queue.get()
            logger.info(f"Received task id=`{task_id}`.")

            is_task_cancelled = await task_queue.is_task_cancelled(task_id)
            if is_task_cancelled:
                continue

            running_tasks_observer.take_slot()
            running_task = loop.create_task(
                handle_cpu_bound_task(
                    task_repository,
                    executor_task_data_storage,
                    process_pool_executor,
                    execution_config,
                    task_id
                )
            )
            running_task.add_done_callback(lambda _: running_tasks_observer.return_slot())

        else:
            await asyncio.sleep(2.)
