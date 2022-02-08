from aiohttp import web

from app.api.model import Error
from app.api.model import TaskInfo
from app.api.serialization import serialize

HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_NOT_FOUND = 404

CONTENT_TYPE_PLAIN_TEXT = "plain/text"
CONTENT_TYPE_APPLICATION_JSON = "application/json"


class HealthCheckResponse(web.Response):
    def __init__(self):
        super().__init__(
            status=HTTP_STATUS_OK,
            headers={
                "content-type": CONTENT_TYPE_PLAIN_TEXT
            },
            body="Hello! I`m OK."
        )


class CreateTaskResponse(web.Response):
    def __init__(self, task_info: TaskInfo):
        super().__init__(
            status=HTTP_STATUS_CREATED,
            headers={
                "content-type": CONTENT_TYPE_APPLICATION_JSON
            },
            body=serialize(task_info)
        )


class BaseErrorResponse(web.Response):
    def __init__(self, error: Error):
        super().__init__(
            status=error.code,
            headers={
                "content-type": CONTENT_TYPE_APPLICATION_JSON
            },
            body=serialize(error)
        )


class NoSuchTaskResponse(BaseErrorResponse):
    def __init__(self, task_id: int):
        error = Error(
            code=HTTP_STATUS_NOT_FOUND,
            message=f"There is no task with such id=`{task_id}`",
            description=None
        )
        super().__init__(error)


class NoTaskOutputDataResponse(BaseErrorResponse):
    def __init__(self, task_id: int):
        error = Error(
            code=HTTP_STATUS_BAD_REQUEST,
            message=f"There is no task with such id=`{task_id}`",
            description=None
        )
        super().__init__(error)
