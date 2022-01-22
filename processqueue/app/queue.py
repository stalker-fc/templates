import asyncio
import os
import signal
from concurrent.futures import ProcessPoolExecutor

from aiohttp.web import Application

from app.common import Result
from app.model import TaskStatus
from app.repository import ITaskRepository
from app.storage import IExecutorTaskDataStorage, DummyExecutorTaskDataStorage, build_executor_task_data_storage, \
    ExecutorTaskDataStorageConfig
from app.executor import execute_task as worker_handle_task, ExecutionConfig


async def handle_task(
        task_repository: ITaskRepository,
        executor_task_data_storage: IExecutorTaskDataStorage,
        process_pool_executor: ProcessPoolExecutor,
        execution_config: ExecutionConfig,
        task_id: int
):
    loop = asyncio.get_event_loop()
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
        worker_config: ExecutionConfig
):
    loop = asyncio.get_event_loop()
    while True:
        task_id: int = await task_queue.get()

        loop.create_task(
            handle_task(
                task_repository,
                worker_task_data_storage,
                process_pool_executor,
                worker_config,
                task_id
            )
        )

        await task_repository.set_task_status(task_id, TaskStatus.QUEUED)

        task_queue.task_done()


def register_signal_handler() -> None:
    signal.signal(signal.SIGSEGV, lambda _, __: print("Mne kapets"))


async def queue_listener_process(app: Application) -> None:
    task_queue = asyncio.Queue()
    app["task_queue"] = task_queue
    task_repository: ITaskRepository = app.get("task_repository")

    process_pool_executor = ProcessPoolExecutor(
        initializer=register_signal_handler,
        max_workers=2
    )

    worker_task_data_storage_config = ExecutorTaskDataStorageConfig()
    worker_config = ExecutionConfig(
        worker_task_data_storage_config
    )
    worker_task_data_storage: IExecutorTaskDataStorage = build_executor_task_data_storage(
        worker_task_data_storage_config
    )

    loop = asyncio.get_event_loop()
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
