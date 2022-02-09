import asyncio
import json

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
def first_task_input_data() -> Dict[str, str]:
    return {
        "input_data": "First Task"
    }


async def test_create_task(client, first_task_input_data: str):
    resp = await client.post(
        '/tasks/create',
        json=json.dumps(first_task_input_data)
    )
    assert resp.status == 201
    assert resp.headers.get("Content-Type") == "application/json"


async def test_create_and_run_task(client, first_task_input_data):
    resp = await client.post(
        "/tasks/create",
        json=json.dumps(first_task_input_data)
    )
    assert resp.status == 201
    assert resp.headers.get("Content-Type") == "application/json"
    data = await resp.json()

    task_id = data["task_id"]

    run_task_data = {
        "task_id": task_id
    }
    resp = await client.post(
        "/tasks/run",
        json=run_task_data
    )
    assert resp.status == 200
    assert resp.headers.get("Content-Type") == "application/json"

    while True:
        resp = await client.get(
            f"/tasks/{task_id}/status"
        )
        data = await resp.json()
        if data["status"] == "SUCCESS" or data["status"] == "FAILURE":
            break
        await asyncio.sleep(0.5)

    resp = await client.get(
        f"/tasks/{task_id}/output"
    )
    data = await resp.json()
    assert data["output_data"] == f"{first_task_input_data['input_data']} - successfully executed"
