"""
Unit tests for the Task Manager API.
Run with: pytest
"""

import pytest
from app import create_app
from models import db


@pytest.fixture
def client():
    """Creates a fresh in-memory database for every test, so tests don't affect each other."""
    app = create_app(db_uri="sqlite:///:memory:")
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task_success(client):
    response = client.post("/tasks", json={"title": "Write report", "status": "pending"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Write report"
    assert data["status"] == "pending"
    assert "id" in data


def test_create_task_missing_title(client):
    response = client.post("/tasks", json={"description": "no title here"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_task_invalid_status(client):
    response = client.post("/tasks", json={"title": "Bad status", "status": "not_a_real_status"})
    assert response.status_code == 400


def test_get_single_task(client):
    create_resp = client.post("/tasks", json={"title": "Read book"})
    task_id = create_resp.get_json()["id"]

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["title"] == "Read book"


def test_get_nonexistent_task(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_update_task(client):
    create_resp = client.post("/tasks", json={"title": "Old title"})
    task_id = create_resp.get_json()["id"]

    update_resp = client.put(f"/tasks/{task_id}", json={"title": "New title", "status": "completed"})
    assert update_resp.status_code == 200
    data = update_resp.get_json()
    assert data["title"] == "New title"
    assert data["status"] == "completed"


def test_update_nonexistent_task(client):
    response = client.put("/tasks/9999", json={"title": "Ghost task"})
    assert response.status_code == 404


def test_delete_task(client):
    create_resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_resp.get_json()["id"]

    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404


def test_delete_nonexistent_task(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404

def test_create_task_with_priority(client):
    response = client.post("/tasks", json={
        "title": "Important task",
        "priority": "high"
    })

    assert response.status_code == 201
    assert response.get_json()["priority"] == "high"

def test_update_task_priority(client):
    response = client.post("/tasks", json={
        "title": "Learn Python"
    })
    task_id = response.get_json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={"priority": "high"}
    )

    assert update_response.status_code == 200
    assert update_response.get_json()["priority"] == "high"