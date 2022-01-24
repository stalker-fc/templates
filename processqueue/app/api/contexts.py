import asyncio
from concurrent.futures import ProcessPoolExecutor

from aiohttp import web

from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.listener import task_queue_listener
from app.execution.storage import ExecutorTaskDataStorageConfig
from app.execution.storage import IExecutorTaskDataStorage
from app.execution.storage import build_executor_task_data_storage


async def task_queue_context(app: web.Application) -> None:
    task_message_queue: asyncio.Queue = app.get("task_message_queue")
    task_repository: ITaskRepository = app.get("task_repository")
    execution_config: ExecutionConfig = app.get("execution_config")
    executor_task_data_storage_config: ExecutorTaskDataStorageConfig = app.get("executor_task_data_storage_config")

    max_running_tasks = app.get("max_running_tasks")
    process_pool_executor = ProcessPoolExecutor(
        max_workers=max_running_tasks
    )

    executor_task_data_storage: IExecutorTaskDataStorage = build_executor_task_data_storage(
        executor_task_data_storage_config
    )

    loop = asyncio.get_running_loop()
    listen_task = loop.create_task(
        task_queue_listener(
            task_message_queue,
            task_repository,
            executor_task_data_storage,
            process_pool_executor,
            execution_config,
            max_running_tasks
        )
    )

    yield

    listen_task.cancel()
    process_pool_executor.shutdown(wait=True)
