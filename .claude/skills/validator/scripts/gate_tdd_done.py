"""
Gate: TDD subtask must be marked done before validator can run.
Usage: python gate_tdd_done.py <task_id>
Exits 0 if safe to proceed, 1 if blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: gate_tdd_done.py <task_id>")
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

# skip if validator already done
if subtask_map.get("validator", {}).get("done"):
    print(f"SKIP: validator already done for {task_id}")
    sys.exit(0)

# check dependency: tdd must be done
if not subtask_map.get("tdd", {}).get("done"):
    print(f"BLOCKED: tdd not marked done for {task_id} — run tdd skill first")
    sys.exit(1)

decisions_file = Path(f"memory/{task_id}_decisions.json")
if not decisions_file.exists():
    print(f"BLOCKED: memory/{task_id}_decisions.json not found — TDD did not write decisions")
    sys.exit(1)

subprocess.run(
    ["python", ".claude/skills/scripts/mark_gate.py", task_id, "validator", "gate_tdd_done"],
    check=True,
)
print(f"OK: tdd done for {task_id}, ready to validate")
sys.exit(0)
