import os

from aiohttp import web

from app.api.contexts import task_queue_context
from app.api.views import cancel_task
from app.api.views import get_task_output_data
from app.api.views import get_task_status
from app.api.views import healthcheck
from app.api.views import create_task
from app.api.views import run_task
from app.domain.repository import build_task_repository
from app.execution.executor import ExecutionConfig
from app.execution.queue import build_long_task_queue
from app.execution.queue import build_task_queue
from app.execution.storage import ExecutorTaskDataStorageConfig


def configure_dependencies(app: web.Application) -> None:
    app["max_running_tasks"] = int(os.getenv("MAX_RUNNING_TASKS", "2"))
    app["executor_task_data_storage_config"] = ExecutorTaskDataStorageConfig()
    app["execution_config"] = ExecutionConfig(app["executor_task_data_storage_config"])
    app["task_message_queue"] = build_task_queue()
    app["long_task_message_queue"] = build_long_task_queue()
    app["task_repository"] = build_task_repository()


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
