import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_tasks(client: AsyncClient):
    # Create a task
    response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test task",
            "category": "work",
            "urgency": "high",
        },
    )
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Test task"
    assert task["category"] == "work"
    task_id = task["id"]

    # List tasks
    response = await client.get("/api/v1/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert any(t["id"] == task_id for t in tasks)


@pytest.mark.asyncio
async def test_update_task_status(client: AsyncClient):
    response = await client.post(
        "/api/v1/tasks",
        json={"title": "Status test task", "category": "personal"},
    )
    task_id = response.json()["id"]

    response = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "done"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
