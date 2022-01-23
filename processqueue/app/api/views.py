import asyncio

from aiohttp import web

from app.domain.repository import ITaskRepository



async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(
        status=200,
        headers={
            "content-type": "plain/text"
        },
        body=str("I`m alive.")
    )


async def upload_content(request: web.Request):
    data = await request.json()
    input_data = data.get("input_data", "")

    task_repository: ITaskRepository = request.app.get("task_repository")
    task = await task_repository.create_task(input_data)

    task_queue: asyncio.Queue = request.app.get("task_queue")
    await task_queue.put(task.task_id)

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
    except Exception as e:
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


async def download_content(request: web.Request):
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
            status=404,
            headers={
                "content-type": "application/json"
            },
            body=str(
                {
                    "error": "Task output data is not exist."
                }
            )
        )
