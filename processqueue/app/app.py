import asyncio

from aiohttp import web

from app.contexts import task_queue_context
from app.repository import DummyTaskRepository
from app.storage import DummyRepositoryTaskDataStorage
from app.views import download_content
from app.views import get_task_status
from app.views import healthcheck
from app.views import upload_content


def configure_dependencies(app: web.Application) -> None:
    app["task_queue"] = asyncio.Queue()
    repository_task_data_storage = DummyRepositoryTaskDataStorage()
    app["task_repository"] = DummyTaskRepository(repository_task_data_storage)


def configure_context(app: web.Application) -> None:
    app.cleanup_ctx.append(task_queue_context)


def configure_routes(app: web.Application) -> None:
    routes = [
        web.get("/", healthcheck),
        web.get("/healthcheck", healthcheck),
        web.post("/upload", upload_content),
        web.get("/status/{task_id:[0-9]+}", get_task_status, allow_head=False),
        web.get("/download/{task_id:[0-9]+}", download_content, allow_head=False),
    ]

    app.add_routes(routes)


def startup_app():
    app = web.Application()

    configure_dependencies(app)
    configure_context(app)
    configure_routes(app)

    return app
