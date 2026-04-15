"""
Tests for write_validation.py summary field support.

Covers:
- summary field present in payload → written to validation file
- summary field absent → empty string written, no failure
- existing human_approved record still blocks overwrite
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / ".claude/skills/validator/scripts/write_validation.py"

BASE_PAYLOAD = {
    "task_id": "test-task",
    "passed": True,
    "checks": {
        "spec_coverage":         {"passed": True, "notes": "ok"},
        "constraint_compliance": {"passed": True, "notes": "ok"},
        "test_validity":         {"passed": True, "notes": "ok"},
        "impl_correctness":      {"passed": True, "notes": "ok"},
    },
    "findings": [],
}


def run_script(payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), json.dumps(payload)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def test_summary_field_written(tmp_path: Path):
    payload = {**BASE_PAYLOAD, "summary": "Five posts written in your brand voice."}
    result = run_script(payload, tmp_path)
    assert result.returncode == 0, result.stderr
    out_file = tmp_path / "memory" / "test-task_validation.json"
    assert out_file.exists()
    record = json.loads(out_file.read_text())
    assert record["summary"] == "Five posts written in your brand voice."


def test_summary_absent_writes_empty_string(tmp_path: Path):
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "summary"}
    result = run_script(payload, tmp_path)
    assert result.returncode == 0, result.stderr
    out_file = tmp_path / "memory" / "test-task_validation.json"
    record = json.loads(out_file.read_text())
    assert record["summary"] == ""


def test_summary_none_writes_empty_string(tmp_path: Path):
    payload = {**BASE_PAYLOAD, "summary": None}
    result = run_script(payload, tmp_path)
    assert result.returncode == 0, result.stderr
    out_file = tmp_path / "memory" / "test-task_validation.json"
    record = json.loads(out_file.read_text())
    assert record["summary"] == ""


def test_approved_record_blocks_overwrite(tmp_path: Path):
    # First write — succeeds
    payload = {**BASE_PAYLOAD, "summary": "First write."}
    run_script(payload, tmp_path)

    # Approve the record manually
    out_file = tmp_path / "memory" / "test-task_validation.json"
    record = json.loads(out_file.read_text())
    record["human_approved"] = True
    out_file.write_text(json.dumps(record))

    # Second write — must be blocked
    payload2 = {**BASE_PAYLOAD, "summary": "Second write attempt."}
    result = run_script(payload2, tmp_path)
    assert result.returncode == 1
    assert "already" in result.stdout.lower() or "approved" in result.stdout.lower()
