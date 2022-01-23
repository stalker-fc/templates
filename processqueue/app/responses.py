from aiohttp import web


class HealthCheckResponse(web.Response):
    ...


class NoSuchTaskResponse(web.Response):
    ...
