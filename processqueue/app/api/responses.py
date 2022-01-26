from aiohttp import web

from app.api.model import TaskInfo

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
            body=TaskInfo.schema().dumps(task_info)
        )




class BaseErrorResponse(web.Response):
    def __init__(self, task_id: int):
        super().__init__(
            status=HTTP_STATUS_NOT_FOUND,
            headers={
                "content-type": CONTENT_TYPE_APPLICATION_JSON
            },
            body="Hello! I`m OK."
        )


class NoSuchTaskResponse(web.Response):
    def __init__(self, task_id: int):
        super().__init__(
            status=HTTP_STATUS_NOT_FOUND,
            headers={
                "content-type": CONTENT_TYPE_APPLICATION_JSON
            },
            body="Hello! I`m OK."
        )

