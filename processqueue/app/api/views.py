import asyncio

from aiohttp import web

from app.api import controller
from app.api.model import TaskInputData
from app.api.responses import CreateTaskResponse
from app.api.responses import HealthCheckResponse
from app.api.responses import IncorrectTaskOperationResponse
from app.api.responses import NoSuchTaskResponse
from app.api.responses import TaskInfoResponse
from app.api.responses import TaskOutputDataResponse
from app.api.serialization import deserialize
from app.domain.repository import ITaskRepository
from app.exceptions import IncorrectTaskOperationException
from app.exceptions import NoSuchTaskException


async def healthcheck(_: web.Request) -> HealthCheckResponse:
    return HealthCheckResponse()


async def create_task(request: web.Request):
    data = await request.json()
    task_input_data = deserialize(TaskInputData, data)
    task_repository: ITaskRepository = request.app.get("task_repository")
    task_info = await controller.create_task(task_repository, task_input_data)
    return CreateTaskResponse(task_info)


async def run_task(request: web.Request):
    data = await request.json()
    task_id = data.get("task_id", "")
    task_queue: asyncio.Queue = request.app.get("task_queue")
    task_repository: ITaskRepository = request.app.get("task_repository")
    try:
        task_info = await controller.run_task(task_repository, task_queue, task_id)
        return TaskInfoResponse(task_info)
    except NoSuchTaskException:
        return NoSuchTaskResponse(task_id)
    except IncorrectTaskOperationException:
        return IncorrectTaskOperationResponse(task_id)


async def cancel_task(request: web.Request):
    data = await request.json()
    task_id = data.get("task_id", "")
    task_repository: ITaskRepository = request.app.get("task_repository")
    try:
        task_info = await controller.cancel_task(task_repository, task_id)
        return TaskInfoResponse(task_info)
    except NoSuchTaskException:
        return NoSuchTaskResponse(task_id)
    except IncorrectTaskOperationException:
        return IncorrectTaskOperationResponse(task_id)


async def get_task_status(request: web.Request):
    task_id = int(request.match_info["task_id"])
    task_repository: ITaskRepository = request.app.get("task_repository")
    try:
        task_info = await controller.get_task_status(task_repository, task_id)
        return TaskInfoResponse(task_info)
    except NoSuchTaskException:
        return NoSuchTaskResponse(task_id)


async def get_task_output_data(request: web.Request):
    task_id = int(request.match_info["task_id"])
    task_repository: ITaskRepository = request.app.get("task_repository")
    try:
        output_data = await controller.get_task_output_data(task_repository, task_id)
        return TaskOutputDataResponse(output_data)
    except NoSuchTaskException:
        return NoSuchTaskResponse(task_id)
    except IncorrectTaskOperationException:
        return IncorrectTaskOperationResponse(task_id)
