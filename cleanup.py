"""
cleanup.py — post-run state wiper.

Usage:
    python cleanup.py <task_id> --approved | --rejected
"""
import argparse
import json
import sys
from pathlib import Path


def _delete_memory_files(task_id: str, root: Path) -> None:
    memory = root / "memory"
    for name in (
        f"{task_id}_context.json",
        f"{task_id}_decisions.json",
        f"{task_id}_validation.json",
        "run_log.jsonl",
        "waiting_for_human.json",
    ):
        (memory / name).unlink(missing_ok=True)


def _reset_tasks_json(root: Path) -> None:
    (root / "tasks.json").write_text('{"tasks": []}')


def cleanup_approved(task_id: str, root: Path = Path(".")) -> None:
    _delete_memory_files(task_id, root)
    (root / "spec.md").unlink(missing_ok=True)
    _reset_tasks_json(root)


def cleanup_rejected(task_id: str, root: Path = Path(".")) -> None:
    # Read deliverable path before deleting memory files
    impl_file = None
    decisions_file = root / "memory" / f"{task_id}_decisions.json"
    try:
        decisions = json.loads(decisions_file.read_text())
        impl_file = decisions.get("entries", [{}])[0].get("impl_file")
    except (FileNotFoundError, IndexError, KeyError, json.JSONDecodeError):
        pass

    _delete_memory_files(task_id, root)

    if impl_file:
        (root / impl_file).unlink(missing_ok=True)

    _reset_tasks_json(root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Wipe harness run state.")
    parser.add_argument("task_id", help="Task ID, e.g. task-1")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--approved", action="store_true")
    group.add_argument("--rejected", action="store_true")
    args = parser.parse_args()

    root = Path(".")
    if args.approved:
        cleanup_approved(args.task_id, root)
    else:
        cleanup_rejected(args.task_id, root)


if __name__ == "__main__":
    main()
