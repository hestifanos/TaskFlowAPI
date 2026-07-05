"""End-to-end API tests using an isolated temporary database."""
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.database as database

# Point the app at a throwaway database before importing routes.
_tmp = Path(tempfile.mkdtemp()) / "test.db"
database.DB_PATH = _tmp

from app.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    if _tmp.exists():
        _tmp.unlink()
    database.init_db(_tmp)
    yield


def register(email="a@example.com", password="password123"):
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_register_rejects_duplicate_email():
    register()
    r = client.post("/api/auth/register", json={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 409


def test_login_wrong_password():
    register()
    r = client.post("/api/auth/login", json={"email": "a@example.com", "password": "wrongpass1"})
    assert r.status_code == 401


def test_task_crud_cycle():
    headers = register()
    created = client.post("/api/tasks", json={"title": "Write tests"}, headers=headers).json()
    assert created["status"] == "todo"

    updated = client.put(f"/api/tasks/{created['id']}",
                         json={"title": "Write tests", "status": "done"}, headers=headers)
    assert updated.json()["status"] == "done"

    assert client.delete(f"/api/tasks/{created['id']}", headers=headers).status_code == 204
    assert client.get("/api/tasks", headers=headers).json() == []


def test_users_cannot_see_each_others_tasks():
    alice = register("alice@example.com")
    bob = register("bob@example.com")
    task = client.post("/api/tasks", json={"title": "secret"}, headers=alice).json()

    assert client.get("/api/tasks", headers=bob).json() == []
    assert client.delete(f"/api/tasks/{task['id']}", headers=bob).status_code == 404


def test_requests_without_token_rejected():
    assert client.get("/api/tasks").status_code == 401
