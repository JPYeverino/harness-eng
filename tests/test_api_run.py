"""
Tests for GET /api/run endpoint in dashboard.py.

Uses FastAPI TestClient with a tmp_path fixture to isolate file state.
"""
import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def make_client(tmp_path: Path) -> TestClient:
    from dashboard import create_app
    app = create_app(root=str(tmp_path))
    return TestClient(app)


def write_tasks(tmp_path: Path, tasks: list) -> None:
    (tmp_path / "tasks.json").write_text(json.dumps({"tasks": tasks}))


def write_validation(tmp_path: Path, task_id: str, data: dict) -> None:
    mem = tmp_path / "memory"
    mem.mkdir(exist_ok=True)
    (mem / f"{task_id}_validation.json").write_text(json.dumps(data))


BASE_TASK = {
    "id": "task-1",
    "title": "Test task",
    "description": "desc",
    "done": False,
    "dependsOn": [],
    "subtasks": [],
    "stack": {"language": "Python", "test_runner": "pytest", "test_command": "pytest -v"},
}

BASE_VALIDATION = {
    "task_id": "task-1",
    "passed": True,
    "summary": "",
    "checks": {
        "spec_coverage":         {"passed": True, "notes": "ok"},
        "constraint_compliance": {"passed": True, "notes": "ok"},
        "test_validity":         {"passed": True, "notes": "ok"},
        "impl_correctness":      {"passed": True, "notes": "ok"},
    },
    "findings": [],
    "human_approved": False,
}


def test_returns_404_when_no_tasks(tmp_path: Path):
    write_tasks(tmp_path, [])
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.status_code == 404


def test_awaiting_approval_false_when_no_gate_tdd_done(tmp_path: Path):
    task = {**BASE_TASK, "subtasks": [{"skill": "tdd", "done": False, "gates": {}}]}
    write_tasks(tmp_path, [task])
    write_validation(tmp_path, "task-1", BASE_VALIDATION)
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.status_code == 200
    assert r.json()["awaiting_approval"] is False


def test_awaiting_approval_true_when_gate_tdd_done_stamped(tmp_path: Path):
    task = {
        **BASE_TASK,
        "subtasks": [{"skill": "tdd", "done": True, "gates": {"gate_tdd_done": True}},
                     {"skill": "validator", "done": False, "gates": {"gate_tdd_done": True}}],
    }
    write_tasks(tmp_path, [task])
    write_validation(tmp_path, "task-1", {**BASE_VALIDATION, "human_approved": False})
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.status_code == 200
    assert r.json()["awaiting_approval"] is True


def test_awaiting_approval_false_when_already_approved(tmp_path: Path):
    task = {
        **BASE_TASK,
        "subtasks": [{"skill": "validator", "done": True, "gates": {"gate_tdd_done": True}}],
    }
    write_tasks(tmp_path, [task])
    write_validation(tmp_path, "task-1", {**BASE_VALIDATION, "human_approved": True})
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.status_code == 200
    assert r.json()["awaiting_approval"] is False


def test_total_checks_and_checks_passed(tmp_path: Path):
    write_tasks(tmp_path, [BASE_TASK])
    write_validation(tmp_path, "task-1", BASE_VALIDATION)
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.status_code == 200
    data = r.json()
    assert data["total_checks"] == 4
    assert data["checks_passed"] == 4


def test_checks_passed_counts_only_true(tmp_path: Path):
    validation = {
        **BASE_VALIDATION,
        "checks": {
            "spec_coverage":         {"passed": True,  "notes": "ok"},
            "constraint_compliance": {"passed": False, "notes": "fail"},
            "test_validity":         {"passed": True,  "notes": "ok"},
            "impl_correctness":      {"passed": False, "notes": "fail"},
        },
    }
    write_tasks(tmp_path, [BASE_TASK])
    write_validation(tmp_path, "task-1", validation)
    client = make_client(tmp_path)
    r = client.get("/api/run")
    data = r.json()
    assert data["total_checks"] == 4
    assert data["checks_passed"] == 2


def test_all_approved_true_when_all_tasks_approved(tmp_path: Path):
    task2 = {**BASE_TASK, "id": "task-2"}
    write_tasks(tmp_path, [BASE_TASK, task2])
    write_validation(tmp_path, "task-1", {**BASE_VALIDATION, "human_approved": True})
    write_validation(tmp_path, "task-2", {**BASE_VALIDATION, "task_id": "task-2", "human_approved": True})
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.json()["all_approved"] is True


def test_all_approved_false_when_one_not_approved(tmp_path: Path):
    task2 = {**BASE_TASK, "id": "task-2"}
    write_tasks(tmp_path, [BASE_TASK, task2])
    write_validation(tmp_path, "task-1", {**BASE_VALIDATION, "human_approved": True})
    write_validation(tmp_path, "task-2", {**BASE_VALIDATION, "task_id": "task-2", "human_approved": False})
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.json()["all_approved"] is False


def test_summaries_returns_nonempty_strings(tmp_path: Path):
    task2 = {**BASE_TASK, "id": "task-2"}
    write_tasks(tmp_path, [BASE_TASK, task2])
    write_validation(tmp_path, "task-1", {**BASE_VALIDATION, "summary": "First summary."})
    write_validation(tmp_path, "task-2", {**BASE_VALIDATION, "task_id": "task-2", "summary": ""})
    client = make_client(tmp_path)
    r = client.get("/api/run")
    data = r.json()
    assert data["summaries"] == ["First summary."]


def test_task_ids_list(tmp_path: Path):
    task2 = {**BASE_TASK, "id": "task-2"}
    write_tasks(tmp_path, [BASE_TASK, task2])
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.json()["task_ids"] == ["task-1", "task-2"]


def test_returns_200_when_validation_files_missing(tmp_path: Path):
    write_tasks(tmp_path, [BASE_TASK])
    # No validation file written
    client = make_client(tmp_path)
    r = client.get("/api/run")
    assert r.status_code == 200
    data = r.json()
    assert data["total_checks"] == 0
    assert data["checks_passed"] == 0
    assert data["summaries"] == []
