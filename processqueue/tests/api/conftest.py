import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient

from app import startup_app


@pytest.fixture
async def app() -> web.Application:
    app = await startup_app()
    return app


@pytest.fixture
def client(
        loop,  # fixture from pytest-aiohttp plugin
        aiohttp_client,  # fixture from pytest-aiohttp plugin
        app: web.Application
) -> TestClient:
    return loop.run_until_complete(aiohttp_client(app))
