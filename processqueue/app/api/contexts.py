import asyncio
import signal
from concurrent.futures import ProcessPoolExecutor

from aiohttp import web

from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.queue import task_queue_listener
from app.execution.storage import ExecutorTaskDataStorageConfig
from app.execution.storage import IExecutorTaskDataStorage
from app.execution.storage import build_executor_task_data_storage



async def task_queue_context(app: web.Application) -> None:
    task_queue: asyncio.Queue = app.get("task_queue")
    task_repository: ITaskRepository = app.get("task_repository")

    process_pool_executor = ProcessPoolExecutor(
        max_workers=2
    )

    worker_task_data_storage_config = ExecutorTaskDataStorageConfig()
    worker_config = ExecutionConfig(
        worker_task_data_storage_config
    )
    worker_task_data_storage: IExecutorTaskDataStorage = build_executor_task_data_storage(
        worker_task_data_storage_config
    )

    loop = asyncio.get_running_loop()
    input_queue_listener_task = loop.create_task(
        task_queue_listener(
            task_queue,
            task_repository,
            worker_task_data_storage,
            process_pool_executor,
            worker_config,
        )
    )

    yield

    input_queue_listener_task.cancel()
    process_pool_executor.shutdown(wait=True)
