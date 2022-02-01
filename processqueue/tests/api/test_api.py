import pytest
from typing import Dict


async def test_index(client):
    resp = await client.get('/')
    assert resp.status == 200
    assert await resp.text() == "Hello! I`m OK."


async def test_healthcheck(client):
    resp = await client.get('/healthcheck')
    assert resp.status == 200
    assert await resp.text() == "Hello! I`m OK."



@pytest.fixture
async def first_task_input_data() -> Dict[str, str]:
    return {
        "input_data": "First Task"
    }


async def test_create_task(client, first_task_input_data: str):
    resp = await client.post(
        '/tasks/create',
        json=first_task_input_data
    )
    assert resp.status == 201
    assert resp.headers.get("Content-Type") == "application/json"
