"""
Tests for task-2: cleanup.py script.
"""
import json
from pathlib import Path

import pytest


def setup_run_state(tmp_path: Path, task_id: str = "task-1", with_deliverable: bool = True) -> Path:
    """Create the expected run state files in tmp_path."""
    memory = tmp_path / "memory"
    memory.mkdir()

    (memory / f"{task_id}_context.json").write_text('{"what": "something"}')
    (memory / f"{task_id}_decisions.json").write_text(
        json.dumps({
            "entries": [{"impl_file": "output/result.md"}]
        })
    )
    (memory / f"{task_id}_validation.json").write_text('{"human_approved": true}')
    (memory / "run_log.jsonl").write_text('{"ts": "2026-01-01"}\n')
    (memory / "waiting_for_human.json").write_text('{}')

    tasks_json = tmp_path / "tasks.json"
    tasks_json.write_text(json.dumps({"tasks": [{"id": task_id, "done": True}]}))

    spec = tmp_path / "spec.md"
    spec.write_text("# Spec")

    if with_deliverable:
        output = tmp_path / "output"
        output.mkdir()
        (output / "result.md").write_text("# Result")

    return tmp_path


def run_cleanup(tmp_path: Path, task_id: str, mode: str):
    """Import and run cleanup module directly against tmp_path."""
    import importlib
    import sys
    import types

    # Load cleanup.py from the project root dynamically
    cleanup_path = Path(__file__).parent.parent / "cleanup.py"
    spec = importlib.util.spec_from_file_location("cleanup", cleanup_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Call the appropriate function
    if mode == "--approved":
        mod.cleanup_approved(task_id, root=tmp_path)
    else:
        mod.cleanup_rejected(task_id, root=tmp_path)


# ── --approved mode ───────────────────────────────────────────────────────────

def test_approved_deletes_memory_files(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--approved")

    memory = tmp_path / "memory"
    assert not (memory / "task-1_context.json").exists()
    assert not (memory / "task-1_decisions.json").exists()
    assert not (memory / "task-1_validation.json").exists()
    assert not (memory / "run_log.jsonl").exists()
    assert not (memory / "waiting_for_human.json").exists()


def test_approved_deletes_spec(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--approved")
    assert not (tmp_path / "spec.md").exists()


def test_approved_resets_tasks_json(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--approved")
    data = json.loads((tmp_path / "tasks.json").read_text())
    assert data == {"tasks": []}


def test_approved_leaves_output_untouched(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--approved")
    assert (tmp_path / "output" / "result.md").exists()


def test_approved_idempotent(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--approved")
    run_cleanup(tmp_path, "task-1", "--approved")  # second run should not raise


# ── --rejected mode ───────────────────────────────────────────────────────────

def test_rejected_deletes_memory_files(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--rejected")

    memory = tmp_path / "memory"
    assert not (memory / "task-1_context.json").exists()
    assert not (memory / "task-1_decisions.json").exists()
    assert not (memory / "task-1_validation.json").exists()
    assert not (memory / "run_log.jsonl").exists()
    assert not (memory / "waiting_for_human.json").exists()


def test_rejected_deletes_deliverable(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--rejected")
    assert not (tmp_path / "output" / "result.md").exists()


def test_rejected_leaves_spec(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--rejected")
    assert (tmp_path / "spec.md").exists()


def test_rejected_resets_tasks_json(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--rejected")
    data = json.loads((tmp_path / "tasks.json").read_text())
    assert data == {"tasks": []}


def test_rejected_idempotent(tmp_path):
    setup_run_state(tmp_path)
    run_cleanup(tmp_path, "task-1", "--rejected")
    run_cleanup(tmp_path, "task-1", "--rejected")  # second run should not raise


def test_rejected_missing_decisions_file_does_not_raise(tmp_path):
    setup_run_state(tmp_path, with_deliverable=False)
    (tmp_path / "memory" / "task-1_decisions.json").unlink()
    run_cleanup(tmp_path, "task-1", "--rejected")  # should not raise
