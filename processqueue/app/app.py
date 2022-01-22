from aiohttp import web

from app.queue import queue_listener_process
from app.repository import DummyTaskRepository
from app.storage import DummyRepositoryTaskDataStorage
from app.views import upload_content, get_task_status, download_content


def startup_app():
    app = web.Application()
    repository_task_data_storage = DummyRepositoryTaskDataStorage()
    app["task_repository"] = DummyTaskRepository(repository_task_data_storage)
    app.cleanup_ctx.append(queue_listener_process)
    app.add_routes(
        [
            web.post("/upload", upload_content),
            web.get("/status/{task_id:[0-9]+}", get_task_status, allow_head=False),
            web.get("/download/{task_id:[0-9]+}", download_content, allow_head=False),
        ]
    )
    return app
