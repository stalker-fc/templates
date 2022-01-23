from aiohttp import web

from app.api.contexts import task_queue_context
from app.api.views import download_content
from app.api.views import get_task_status
from app.api.views import healthcheck
from app.api.views import upload_content
from app.domain.repository import build_task_repository
from app.execution.queue import build_task_queue


def configure_dependencies(app: web.Application) -> None:
    app["task_queue"] = build_task_queue()
    app["task_repository"] = build_task_repository()


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
