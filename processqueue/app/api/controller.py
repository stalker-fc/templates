from app.api.model import TaskInfo
from app.api.model import TaskInputData
from app.api.model import TaskOutputData
from app.domain.model import TaskStatus
from app.domain.queue import ITaskQueue
from app.domain.repository import ITaskRepository
from app.exceptions import IncorrectTaskOperationException


async def create_task(task_repository: ITaskRepository, task_input_data: TaskInputData) -> TaskInfo:
    task = await task_repository.create_task(task_input_data.input_data)
    return TaskInfo(
        task_id=task.task_id,
        status=task.status.value
    )


async def run_task(task_repository: ITaskRepository, task_queue: ITaskQueue, task_id: int) -> TaskInfo:
    task_status = await task_repository.get_task_status(task_id)
    if task_status is TaskStatus.CREATED or task_status is TaskStatus.CANCELLED:
        await task_queue.put(task_id)
        await task_repository.set_task_status(task_id, TaskStatus.QUEUED)
        return TaskInfo(
            task_id=task_id,
            status=TaskStatus.QUEUED.value
        )
    else:
        raise IncorrectTaskOperationException(task_id)


async def cancel_task(task_repository: ITaskRepository, task_queue: ITaskQueue, task_id: int) -> TaskInfo:
    status = await task_repository.get_task_status(task_id)
    if status is TaskStatus.QUEUED:
        await task_queue.cancel(task_id)
        await task_repository.set_task_status(task_id, TaskStatus.CANCELLED)
        return TaskInfo(
            task_id=task_id,
            status=TaskStatus.CANCELLED.value
        )
    else:
        raise IncorrectTaskOperationException(task_id)


async def get_task_status(task_repository: ITaskRepository, task_id: int) -> TaskInfo:
    status = await task_repository.get_task_status(task_id)
    return TaskInfo(
        task_id=task_id,
        status=status.value
    )


async def get_task_output_data(task_repository: ITaskRepository, task_id: int) -> TaskOutputData:
    output_data = await task_repository.get_task_output_data(task_id)
    return TaskOutputData(
        task_id=task_id,
        output_data=output_data
    )
