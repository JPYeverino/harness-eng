"""
Gate: tasks.json must exist and the task must not already have context.
Usage: python gate_task_exists.py <task_id>
Exits 0 if safe to proceed, 1 if blocked.
"""
import json
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: gate_task_exists.py <task_id>")
    sys.exit(1)

if not Path("tasks.json").exists():
    print("BLOCKED: tasks.json not found — run planner first")
    sys.exit(1)

tasks = json.loads(Path("tasks.json").read_text())
task_map = {t["id"]: t for t in tasks["tasks"]}

if task_id not in task_map:
    print(f"BLOCKED: task '{task_id}' not found in tasks.json")
    sys.exit(1)

task = task_map[task_id]

# check planner completed before context can run
if not task.get("completed", {}).get("planner"):
    print(f"BLOCKED: planner not done for {task_id} — run planner first")
    sys.exit(1)

# skip if context already done
if task.get("completed", {}).get("context"):
    print(f"SKIP: context already done for {task_id}")
    sys.exit(0)

print(f"OK: proceed with context for {task_id}")
sys.exit(0)
