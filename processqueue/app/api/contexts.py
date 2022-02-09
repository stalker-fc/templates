import asyncio

from aiohttp import web

from app.domain.listener import ITaskQueueListener


async def task_queue_context(app: web.Application) -> None:
    task_queue_listener: ITaskQueueListener = app.get("task_queue_listener")

    loop = asyncio.get_running_loop()
    listen_task = loop.create_task(
        task_queue_listener.listen()
    )

    yield

    listen_task.cancel()
    task_queue_listener.stop()
