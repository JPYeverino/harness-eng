"""
Tests for task-3: check_tasks_done.py continuation command includes cleanup.py --approved.
"""
from pathlib import Path

HOOK_FILE = Path(__file__).parent.parent / ".claude/skills/orchestrator/scripts/check_tasks_done.py"


def test_hook_file_exists():
    assert HOOK_FILE.exists(), f"Expected {HOOK_FILE} to exist"


def test_continuation_command_includes_cleanup():
    source = HOOK_FILE.read_text()
    assert "cleanup.py" in source, "cleanup.py should appear in continuation command"


def test_continuation_command_includes_approved_flag():
    source = HOOK_FILE.read_text()
    assert "--approved" in source, "--approved should appear in continuation command"


def test_cleanup_follows_mark_done_in_command():
    source = HOOK_FILE.read_text()
    # The approval continuation command must have mark_done before cleanup --approved
    mark_done_pos = source.find("mark_done.py {tid}")
    cleanup_approved_pos = source.find("cleanup.py {tid} --approved")
    assert mark_done_pos != -1, "mark_done.py {tid} should exist in source"
    assert cleanup_approved_pos != -1, "cleanup.py {tid} --approved should exist in source"
    assert cleanup_approved_pos > mark_done_pos, "cleanup.py --approved should appear after mark_done.py in the approval command"
