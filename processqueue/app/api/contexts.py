import asyncio
import signal
from concurrent.futures import ProcessPoolExecutor

from aiohttp import web

from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.listener import TaskMessageQueueListener
from app.execution.storage import ExecutorTaskDataStorageConfig
from app.execution.storage import IExecutorTaskDataStorage
from app.execution.storage import build_executor_task_data_storage



async def task_queue_context(app: web.Application) -> None:
    task_message_queue: asyncio.Queue = app.get("task_message_queue")
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
    task_message_queue_listener = TaskMessageQueueListener(
        task_message_queue,
        task_repository,
        worker_task_data_storage,
        process_pool_executor,
        worker_config,
        max_running_tasks=2
    )

    listen_task = loop.create_task(
        task_message_queue_listener.listen()
    )

    yield

    listen_task.cancel()
    process_pool_executor.shutdown(wait=True)
