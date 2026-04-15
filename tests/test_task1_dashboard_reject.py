"""
Tests for task-1: POST /api/reject/{task_id} endpoint and
conditional sentinel deletion in POST /api/approve/{task_id}.
"""
import json
import pytest
from pathlib import Path
from starlette.testclient import TestClient

from dashboard import create_app


@pytest.fixture
def tmp_app(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    app = create_app(root=str(tmp_path))
    return TestClient(app), tmp_path


# ── /api/reject/{task_id} ─────────────────────────────────────────────────────

def test_reject_sets_human_rejected(tmp_app):
    client, root = tmp_app
    val_file = root / "memory" / "task-1_validation.json"
    val_file.write_text(json.dumps({"passed": True}))

    r = client.post("/api/reject/task-1")
    assert r.status_code == 200
    assert r.json() == {"human_rejected": True}
    data = json.loads(val_file.read_text())
    assert data["human_rejected"] is True


def test_reject_does_not_delete_sentinel(tmp_app):
    client, root = tmp_app
    val_file = root / "memory" / "task-1_validation.json"
    val_file.write_text(json.dumps({"passed": True}))
    sentinel = root / "memory" / "waiting_for_human.json"
    sentinel.write_text(json.dumps({"task_ids": ["task-1"]}))

    r = client.post("/api/reject/task-1")
    assert r.status_code == 200
    assert sentinel.exists(), "sentinel must NOT be deleted by reject"


def test_reject_returns_404_when_no_validation_file(tmp_app):
    client, root = tmp_app
    r = client.post("/api/reject/task-99")
    assert r.status_code == 404


# ── /api/approve conditional sentinel deletion ────────────────────────────────

def test_approve_does_not_delete_sentinel_when_other_tasks_pending(tmp_app):
    client, root = tmp_app
    memory = root / "memory"
    memory.mkdir(exist_ok=True)

    sentinel = memory / "waiting_for_human.json"
    sentinel.write_text(json.dumps({"task_ids": ["task-1", "task-2"]}))

    # Only task-1 validation file exists (task-2 not yet resolved)
    (memory / "task-1_validation.json").write_text(json.dumps({"passed": True}))

    r = client.post("/api/approve/task-1")
    assert r.status_code == 200
    assert sentinel.exists(), "sentinel must NOT be deleted when task-2 is still pending"


def test_approve_deletes_sentinel_when_all_tasks_resolved(tmp_app):
    client, root = tmp_app
    memory = root / "memory"

    sentinel = memory / "waiting_for_human.json"
    sentinel.write_text(json.dumps({"task_ids": ["task-1", "task-2"]}))

    # Both validation files exist; task-2 is already approved
    (memory / "task-1_validation.json").write_text(json.dumps({"passed": True}))
    (memory / "task-2_validation.json").write_text(json.dumps({"human_approved": True}))

    r = client.post("/api/approve/task-1")
    assert r.status_code == 200
    assert not sentinel.exists(), "sentinel MUST be deleted when all tasks resolved"


def test_approve_deletes_sentinel_when_other_task_rejected(tmp_app):
    client, root = tmp_app
    memory = root / "memory"

    sentinel = memory / "waiting_for_human.json"
    sentinel.write_text(json.dumps({"task_ids": ["task-1", "task-2"]}))

    (memory / "task-1_validation.json").write_text(json.dumps({"passed": True}))
    (memory / "task-2_validation.json").write_text(json.dumps({"human_rejected": True}))

    r = client.post("/api/approve/task-1")
    assert r.status_code == 200
    assert not sentinel.exists(), "sentinel MUST be deleted when remaining tasks are rejected"


def test_approve_still_works_without_sentinel(tmp_app):
    client, root = tmp_app
    val_file = root / "memory" / "task-1_validation.json"
    val_file.write_text(json.dumps({"passed": True}))

    r = client.post("/api/approve/task-1")
    assert r.status_code == 200
    assert r.json() == {"human_approved": True}
