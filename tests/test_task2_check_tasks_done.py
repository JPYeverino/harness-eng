"""
Tests for task-2: check_tasks_done.py source assertions.
Verifies the Stop hook contains the required rejection-handling logic.
"""
from pathlib import Path

HOOK_PATH = Path(".claude/skills/orchestrator/scripts/check_tasks_done.py")


def _source() -> str:
    return HOOK_PATH.read_text()


def test_human_rejected_appears_in_source():
    assert "human_rejected" in _source(), (
        "check_tasks_done.py must reference human_rejected to detect rejections"
    )


def test_cleanup_rejected_appears_in_source():
    assert "--rejected" in _source(), (
        "check_tasks_done.py must invoke cleanup.py with --rejected flag"
    )


def test_sentinel_deletion_is_conditional():
    src = _source()
    # The while loop must check _any_rejected() so it exits on rejection too
    assert "_any_rejected" in src, (
        "check_tasks_done.py must define/call _any_rejected() for conditional exit"
    )


def test_polling_loop_exits_on_rejection():
    src = _source()
    # The while condition must include not _any_rejected() (or equivalent)
    assert "not _any_rejected()" in src, (
        "Polling loop must exit when any task is rejected: 'not _any_rejected()'"
    )


def test_sys_exit_2_for_rejected_path():
    src = _source()
    # After detecting rejection there must be a sys.exit(2) call
    # (there is already one for the approval path; need one for rejection too)
    assert src.count("sys.exit(2)") >= 2, (
        "check_tasks_done.py must have sys.exit(2) for both approval and rejection paths"
    )
