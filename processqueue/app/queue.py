import asyncio
import os
from concurrent.futures import ProcessPoolExecutor

from app.common import Result
from app.executor import ExecutionConfig
from app.executor import execute_task as worker_handle_task
from app.model import TaskStatus
from app.repository import ITaskRepository
from app.storage import IExecutorTaskDataStorage


async def handle_task(
        task_repository: ITaskRepository,
        executor_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig,
        task_id: int
):
    loop = asyncio.get_running_loop()
    task = await task_repository.get_task(task_id)
    print(f"handle_task handling task_id={task_id} in process={os.getpid()}")

    executor_task_data_storage.set_input_data(task.task_id, task.input_data)

    result = await loop.run_in_executor(
        process_pool_executor,
        worker_handle_task,
        execution_config,
        task.task_id
    )

    await task_repository.set_task_status(task_id, TaskStatus.RUNNING)

    if result is Result.SUCCESS:
        print("SUCCESS")
        await task_repository.set_task_status(task_id, TaskStatus.SUCCESS)
        await task_repository.add_task_output_data(task_id, "it`s ok")
    else:
        print("FAILURE")
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
