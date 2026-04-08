"""
Gate: context file must exist before TDD can start.
Usage: python gate_context_exists.py <task_id>
Exits 0 if safe to proceed, 1 if blocked.
"""
import json
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: gate_context_exists.py <task_id>")
    sys.exit(1)

# check context marked done in tasks.json
tasks_file = Path("tasks.json")
if tasks_file.exists():
    data = json.loads(tasks_file.read_text())
    task_map = {t["id"]: t for t in data["tasks"]}
    task = task_map.get(task_id, {})
    if not task.get("completed", {}).get("context"):
        print(f"BLOCKED: context skill not marked done for {task_id} — run context skill first")
        sys.exit(1)
    if task.get("completed", {}).get("tdd"):
        print(f"SKIP: tdd already done for {task_id}")
        sys.exit(0)

context_file = Path(f"memory/{task_id}_context.json")
if not context_file.exists():
    print(f"BLOCKED: no context file found for {task_id}")
    sys.exit(1)

print(f"OK: context exists for {task_id}")
sys.exit(0)
