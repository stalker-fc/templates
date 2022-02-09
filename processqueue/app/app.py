import os

from aiohttp import web

from app.api.contexts import task_queue_context
from app.api.views import cancel_task
from app.api.views import create_task
from app.api.views import get_task_output_data
from app.api.views import get_task_status
from app.api.views import healthcheck
from app.api.views import run_task
from app.data import build_task_repository
from app.domain.listener import ITaskQueueListener
from app.domain.queue import ITaskQueue
from app.domain.repository import ITaskRepository
from app.execution.executor import ExecutionConfig
from app.execution.listener import ListenerConfig
from app.execution.listener import build_task_queue_listener
from app.execution.queue import build_task_queue
from app.execution.storage import ExecutorTaskDataStorageConfig


def configure_dependencies(app: web.Application) -> None:
    max_running_tasks = int(os.getenv("MAX_RUNNING_TASKS", "2"))
    executor_task_data_storage_config = ExecutorTaskDataStorageConfig()
    execution_config = ExecutionConfig(executor_task_data_storage_config)
    listener_config = ListenerConfig(
        execution_config=execution_config,
        max_running_tasks=max_running_tasks,
    )

    task_repository: ITaskRepository = build_task_repository()
    task_queue: ITaskQueue = build_task_queue()

    task_queue_listener: ITaskQueueListener = build_task_queue_listener(
        task_repository,
        task_queue,
        listener_config
    )

    app["task_queue"] = task_queue
    app["task_repository"] = task_repository
    app["task_queue_listener"] = task_queue_listener


def configure_context(app: web.Application) -> None:
    app.cleanup_ctx.append(task_queue_context)


def configure_routes(app: web.Application) -> None:
    routes = [
        web.get("/", healthcheck),
        web.get("/healthcheck", healthcheck),
        web.post("/tasks/create", create_task),
        web.post("/tasks/run", run_task),
        web.post("/tasks/cancel", cancel_task),
        web.get("/tasks/{task_id:[0-9]+}/status", get_task_status, allow_head=False),
        web.get("/tasks/{task_id:[0-9]+}/output", get_task_output_data, allow_head=False),
    ]

    app.add_routes(routes)


async def startup_app() -> web.Application:
    app = web.Application()

    configure_dependencies(app)
    configure_context(app)
    configure_routes(app)

    return app
