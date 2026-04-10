"""
Gate: planner subtask must be done before context can run.
Usage: python gate_task_exists.py <task_id>
Exits 0 if safe to proceed, 1 if blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: gate_task_exists.py <task_id>")
    sys.exit(1)

if not Path("tasks.json").exists():
    print("BLOCKED: tasks.json not found — run planner first")
    sys.exit(1)

data = json.loads(Path("tasks.json").read_text())
task_map = {t["id"]: t for t in data["tasks"]}

if task_id not in task_map:
    print(f"BLOCKED: task '{task_id}' not found in tasks.json")
    sys.exit(1)

task = task_map[task_id]
subtask_map = {st["skill"]: st for st in task.get("subtasks", [])}

# skip if context already done
if subtask_map.get("context", {}).get("done"):
    print(f"SKIP: context already done for {task_id}")
    sys.exit(0)

# check dependency: planner must be done
if not subtask_map.get("planner", {}).get("done"):
    print(f"BLOCKED: planner not done for {task_id} — run planner first")
    sys.exit(1)

subprocess.run(
    ["python", ".claude/skills/scripts/mark_gate.py", task_id, "context", "gate_task_exists"],
    check=True,
)
print(f"OK: proceed with context for {task_id}")
sys.exit(0)
