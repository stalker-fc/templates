import asyncio
from concurrent.futures import ProcessPoolExecutor

from app.domain.data import TaskStatus
from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.handler import handle_cpu_bound_task
from app.execution.storage import IExecutorTaskDataStorage
from app.logger import get_logger

logger = get_logger(__name__)


class RunningTasksCounter:
    def __init__(self, max_running_tasks: int):
        self._max_running_tasks = max_running_tasks
        self._current_running_tasks = 0

    def can_run_one_more_task(self) -> bool:
        return self._current_running_tasks < self._max_running_tasks

    def run_new_task(self):
        self._current_running_tasks += 1

    def finish_task(self):
        self._current_running_tasks -= 1


async def task_queue_listener(
        task_queue: asyncio.Queue,
        task_repository: ITaskRepository,
        worker_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig,
        max_running_tasks: int
) -> None:
    loop = asyncio.get_running_loop()
    running_tasks_counter = RunningTasksCounter(max_running_tasks)
    while True:
        if running_tasks_counter.can_run_one_more_task():
            task_id: int = await task_queue.get()
            logger.info(f"Received task id=`{task_id}`.")
            task_status: TaskStatus = await task_repository.get_task_status(task_id)
            if task_status is TaskStatus.QUEUED:
                running_tasks_counter.run_new_task()
                running_task = loop.create_task(
                    handle_cpu_bound_task(
                        task_repository,
                        worker_task_data_storage,
                        process_pool_executor,
                        execution_config,
                        task_id
                    )
                )
                running_task.add_done_callback(lambda _: running_tasks_counter.finish_task())
            task_queue.task_done()
        else:
            await asyncio.sleep(2.)
