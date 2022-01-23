import asyncio
from concurrent.futures import ProcessPoolExecutor

from app.domain.model import TaskStatus
from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.executor import execute_task as worker_handle_task
from app.execution.result import Result
from app.execution.storage import IExecutorTaskDataStorage
from app.logger import get_logger

logger = get_logger(__name__)

async def handle_task(
        task_repository: ITaskRepository,
        executor_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig,
        task_id: int
):
    loop = asyncio.get_running_loop()
    task = await task_repository.get_task(task_id)

    executor_task_data_storage.set_input_data(task.task_id, task.input_data)

    await task_repository.set_task_status(task_id, TaskStatus.RUNNING)
    result = await loop.run_in_executor(
        process_pool_executor,
        worker_handle_task,
        execution_config,
        task.task_id
    )

    if result is Result.SUCCESS:
        logger.info(f"Execution of task id=`{task_id}` is completed successfully.")
        await task_repository.set_task_status(task_id, TaskStatus.SUCCESS)
        output_data = executor_task_data_storage.get_output_data(task_id)
        await task_repository.add_task_output_data(task_id, output_data)
    else:
        logger.info(f"Execution of task id=`{task_id}` is failed.")
        await task_repository.set_task_status(task_id, TaskStatus.FAILURE)


async def task_queue_listener(
        task_queue: asyncio.Queue,
        task_repository: ITaskRepository,
        worker_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig
):
    loop = asyncio.get_running_loop()
    while True:
        task_id: int = await task_queue.get()
        logger.info(f"Received task id=`{task_id}`.")
        loop.create_task(
            handle_task(
                task_repository,
                worker_task_data_storage,
                process_pool_executor,
                execution_config,
                task_id
            )
        )

        await task_repository.set_task_status(task_id, TaskStatus.QUEUED)
        task_queue.task_done()


def build_task_queue() -> asyncio.Queue:
    return asyncio.Queue()
