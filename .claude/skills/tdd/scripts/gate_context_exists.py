"""
Gate: context subtask must be done before TDD can start.
Usage: python gate_context_exists.py <task_id>
Exits 0 if safe to proceed, 1 if blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: gate_context_exists.py <task_id>")
    sys.exit(1)

tasks_file = Path("tasks.json")
if not tasks_file.exists():
    print("BLOCKED: tasks.json not found — run planner first")
    sys.exit(1)

data = json.loads(tasks_file.read_text())
task_map = {t["id"]: t for t in data["tasks"]}
task = task_map.get(task_id)
if not task:
    print(f"BLOCKED: task '{task_id}' not found in tasks.json")
    sys.exit(1)

subtask_map = {st["skill"]: st for st in task.get("subtasks", [])}

# skip if tdd already done
if subtask_map.get("tdd", {}).get("done"):
    print(f"SKIP: tdd already done for {task_id}")
    sys.exit(0)

# check dependency: context must be done
if not subtask_map.get("context", {}).get("done"):
    print(f"BLOCKED: context skill not marked done for {task_id} — run context skill first")
    sys.exit(1)

context_file = Path(f"memory/{task_id}_context.json")
if not context_file.exists():
    print(f"BLOCKED: no context file found for {task_id}")
    sys.exit(1)

subprocess.run(
    ["python", ".claude/skills/scripts/mark_gate.py", task_id, "tdd", "gate_context_exists"],
    check=True,
)
print(f"OK: context exists for {task_id}")
sys.exit(0)
