import asyncio

from aiohttp import web

from app.domain.data import TaskStatus
from app.domain.repository import ITaskRepository
from app.domain.service import CancelTaskMessage
from app.domain.service import RunTaskMessage
from app.exceptions import NoSuchTaskException


async def healthcheck(_: web.Request) -> web.Response:
    return web.Response(
        status=200,
        headers={
            "content-type": "plain/text"
        },
        body=str("I`m alive.")
    )


async def create_task(request: web.Request):
    data = await request.json()
    input_data = data.get("input_data", "")

    task_repository: ITaskRepository = request.app.get("task_repository")
    task = await task_repository.create_task(input_data)

    return web.Response(
        status=200,
        headers={
            "content-type": "application/json"
        },
        body=str(
            {
                "task_id": task.task_id
            }
        )
    )


async def run_task(request: web.Request):
    data = await request.json()
    task_id = data.get("task_id", "")

    task_repository: ITaskRepository = request.app.get("task_repository")
    is_task_exists = await task_repository.is_task_exists(task_id)
    if is_task_exists:
        run_message = RunTaskMessage(task_id)
        task_message_queue: asyncio.Queue = request.app.get("task_message_queue")
        await task_repository.set_task_status(task_id, TaskStatus.QUEUED)
        await task_message_queue.put(run_message)

        return web.Response(
            status=200,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "task_id": task_id
                }
            )
        )
    else:
        return web.Response(
            status=404,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "error": "Task is not exist."
                }
            )
        )


async def cancel_task(request: web.Request):
    data = await request.json()
    task_id = data.get("task_id", "")

    task_repository: ITaskRepository = request.app.get("task_repository")
    status = await task_repository.get_task_status(task_id)

    if status is TaskStatus.QUEUED or status is TaskStatus.RUNNING:
        cancel_message = CancelTaskMessage(task_id)
        task_message_queue: asyncio.Queue = request.app.get("task_message_queue")
        await task_message_queue.put(cancel_message)

        return web.Response(
            status=200,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "task_id": task_id
                }
            )
        )
    else:
        return web.Response(
            status=404,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "error": "Task is not exist."
                }
            )
        )



async def get_task_status(request: web.Request):
    task_id = int(request.match_info['task_id'])
    try:
        task_repository: ITaskRepository = request.app.get("task_repository")
        status = await task_repository.get_task_status(task_id)
        return web.Response(
            status=200,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "task_id": task_id,
                    "status": status.value
                }
            )
        )
    except NoSuchTaskException:
        return web.Response(
            status=404,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "error": "Task is not exist."
                }
            )
        )


async def get_task_output_data(request: web.Request):
    task_id = int(request.match_info['task_id'])
    try:
        task_repository: ITaskRepository = request.app.get("task_repository")
        output_data = await task_repository.get_task_output_data(task_id)
        return web.Response(
            status=200,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "task_id": task_id,
                    "output_data": output_data
                }
            )
        )
    except Exception as e:
        return web.Response(
            status=400,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "error": "Task output data is not exist."
                }
            )
        )
