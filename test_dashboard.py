"""
Tests for the harness dashboard FastAPI app (task-1).
API layer only — no browser tests.
"""
import json
import os
import tempfile
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_root(tmp_path, monkeypatch):
    """Create a temp directory that acts as the project root and chdir into it."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def tasks_json(tmp_root):
    data = {
        "tasks": [
            {
                "id": "task-1",
                "title": "Example Task",
                "done": False,
                "subtasks": [
                    {"id": "task-1.planner", "skill": "planner", "done": True, "gates": {}},
                    {"id": "task-1.tdd", "skill": "tdd", "done": False, "gates": {"gate_context_exists": True}},
                ],
            }
        ]
    }
    (tmp_root / "tasks.json").write_text(json.dumps(data))
    return data


@pytest.fixture()
def memory_files(tmp_root):
    memory = tmp_root / "memory"

    context = {"task_id": "task-1", "what": "build something", "approach": "TDD", "notes": "none"}
    (memory / "task-1_context.json").write_text(json.dumps(context))

    decisions = {"task_id": "task-1", "decisions": ["chose FastAPI", "no DB"]}
    (memory / "task-1_decisions.json").write_text(json.dumps(decisions))

    validation = {"task_id": "task-1", "checks": [{"name": "tests pass", "passed": True}], "human_approved": False}
    (memory / "task-1_validation.json").write_text(json.dumps(validation))

    return {"context": context, "decisions": decisions, "validation": validation}


@pytest.fixture()
def run_log(tmp_root):
    memory = tmp_root / "memory"
    lines = [
        {"timestamp": "2026-01-01T00:00:00Z", "tool": "Read", "input": "file.py", "response": "ok"},
        {"timestamp": "2026-01-01T00:00:01Z", "tool": "Write", "input": "out.py", "response": "written"},
    ]
    (memory / "run_log.jsonl").write_text("\n".join(json.dumps(l) for l in lines))
    return lines


@pytest.fixture()
def client(tmp_root, tasks_json):
    from dashboard import create_app
    app = create_app(root=str(tmp_root))
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/tasks
# ---------------------------------------------------------------------------

class TestGetTasks:
    def test_returns_tasks_json(self, client, tasks_json):
        resp = client.get("/api/tasks")
        assert resp.status_code == 200
        assert resp.json() == tasks_json

    def test_missing_tasks_json_returns_404(self, tmp_root):
        from dashboard import create_app
        app = create_app(root=str(tmp_root))
        c = TestClient(app)
        resp = c.get("/api/tasks")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/memory/{task_id}
# ---------------------------------------------------------------------------

class TestGetMemory:
    def test_merges_context_decisions_validation(self, client, tasks_json, memory_files):
        resp = client.get("/api/memory/task-1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["context"]["what"] == "build something"
        assert body["decisions"]["decisions"] == ["chose FastAPI", "no DB"]
        assert body["validation"]["human_approved"] is False

    def test_missing_task_returns_404(self, client, tasks_json):
        resp = client.get("/api/memory/nonexistent")
        assert resp.status_code == 404

    def test_partial_memory_returns_available_keys(self, client, tasks_json, tmp_root):
        # only context file exists
        memory = tmp_root / "memory"
        context = {"task_id": "task-1", "what": "x", "approach": "y", "notes": "z"}
        (memory / "task-1_context.json").write_text(json.dumps(context))
        resp = client.get("/api/memory/task-1")
        assert resp.status_code == 200
        body = resp.json()
        assert "context" in body
        assert body.get("decisions") is None
        assert body.get("validation") is None


# ---------------------------------------------------------------------------
# GET /api/logs
# ---------------------------------------------------------------------------

class TestGetLogs:
    def test_returns_log_entries_as_array(self, client, tasks_json, run_log):
        resp = client.get("/api/logs")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 2
        assert body[0]["tool"] == "Read"

    def test_missing_log_returns_empty_array(self, client, tasks_json):
        resp = client.get("/api/logs")
        assert resp.status_code == 200
        assert resp.json() == []


# ---------------------------------------------------------------------------
# GET /api/tasks/{task_id}/approval
# ---------------------------------------------------------------------------

class TestGetApproval:
    def test_returns_human_approved_false(self, client, tasks_json, memory_files):
        resp = client.get("/api/tasks/task-1/approval")
        assert resp.status_code == 200
        assert resp.json() == {"human_approved": False}

    def test_returns_human_approved_true_after_approval(self, client, tasks_json, tmp_root):
        memory = tmp_root / "memory"
        validation = {"task_id": "task-1", "checks": [], "human_approved": True}
        (memory / "task-1_validation.json").write_text(json.dumps(validation))
        resp = client.get("/api/tasks/task-1/approval")
        assert resp.status_code == 200
        assert resp.json() == {"human_approved": True}

    def test_missing_validation_returns_false(self, client, tasks_json):
        resp = client.get("/api/tasks/task-1/approval")
        assert resp.status_code == 200
        assert resp.json() == {"human_approved": False}


# ---------------------------------------------------------------------------
# POST /api/approve/{task_id}
# ---------------------------------------------------------------------------

class TestApprove:
    def test_sets_human_approved_true(self, client, tasks_json, memory_files, tmp_root):
        resp = client.post("/api/approve/task-1")
        assert resp.status_code == 200
        validation = json.loads((tmp_root / "memory" / "task-1_validation.json").read_text())
        assert validation["human_approved"] is True

    def test_deletes_sentinel_if_exists(self, client, tasks_json, memory_files, tmp_root):
        sentinel = tmp_root / "memory" / "waiting_for_human.json"
        sentinel.write_text("{}")
        client.post("/api/approve/task-1")
        assert not sentinel.exists()

    def test_approve_missing_task_returns_404(self, client, tasks_json):
        resp = client.post("/api/approve/nonexistent")
        assert resp.status_code == 404

    def test_approval_reflected_in_get_approval(self, client, tasks_json, memory_files):
        client.post("/api/approve/task-1")
        resp = client.get("/api/tasks/task-1/approval")
        assert resp.json() == {"human_approved": True}


# ---------------------------------------------------------------------------
# GET /api/events  (SSE stream)
# Use async httpx + ASGITransport because the sync TestClient blocks on
# infinite streaming responses.
# ---------------------------------------------------------------------------

@pytest.fixture()
def asgi_app(tmp_root, tasks_json):
    from dashboard import create_app
    return create_app(root=str(tmp_root))


class TestSseEvents:
    def test_sse_route_registered(self, asgi_app):
        paths = {r.path for r in asgi_app.routes if hasattr(r, "path")}
        assert "/api/events" in paths

    @pytest.mark.anyio
    async def test_sse_stream_emits_tasks_json_immediately(self, tmp_root, tasks_json):
        from dashboard import tasks_sse_stream
        tasks_file = tmp_root / "tasks.json"
        gen = tasks_sse_stream(tasks_file)
        chunk = await gen.__anext__()
        await gen.aclose()
        assert chunk.startswith("data:")
        payload = json.loads(chunk[len("data:"):].strip())
        assert "tasks" in payload

    @pytest.mark.anyio
    async def test_sse_stream_emits_on_file_change(self, tmp_root, tasks_json):
        from dashboard import tasks_sse_stream
        tasks_file = tmp_root / "tasks.json"
        gen = tasks_sse_stream(tasks_file)
        # First event (initial state)
        await gen.__anext__()
        # Modify the file to trigger a second event
        updated = {**tasks_json, "changed": True}
        tasks_file.write_text(json.dumps(updated))
        chunk = await gen.__anext__()
        await gen.aclose()
        assert chunk.startswith("data:")
        payload = json.loads(chunk[len("data:"):].strip())
        assert payload.get("changed") is True


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestServeDashboard:
    def test_serves_html(self, client, tasks_json, tmp_root):
        (tmp_root / "dashboard.html").write_text("<html><body>dashboard</body></html>")
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
