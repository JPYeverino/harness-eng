"""
Marks a task as done in tasks.json.
Usage: python skills/scripts/mark_done.py <task_id> <skill>

skill is one of: planner, context, tdd
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: mark_done.py <task_id> <skill>")
    sys.exit(1)

task_id = sys.argv[1]
skill = sys.argv[2]

tasks_file = Path("tasks.json")
if not tasks_file.exists():
    print("BLOCKED: tasks.json not found")
    sys.exit(1)

data = json.loads(tasks_file.read_text())
matched = False
for task in data["tasks"]:
    if task["id"] == task_id:
        task.setdefault("completed", {})
        task["completed"][skill] = True
        matched = True
        break

if not matched:
    print(f"BLOCKED: task '{task_id}' not found")
    sys.exit(1)

tasks_file.write_text(json.dumps(data, indent=2))
print(f"Marked {task_id}/{skill} as done")
