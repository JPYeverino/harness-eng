"""
Stamps a gate as passed in tasks.json subtasks.
Called by gate scripts when they exit 0.
Usage: python mark_gate.py <task_id> <skill> <gate_name>
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 4:
    print("Usage: mark_gate.py <task_id> <skill> <gate_name>")
    sys.exit(1)

task_id, skill, gate_name = sys.argv[1], sys.argv[2], sys.argv[3]

tasks_file = Path("tasks.json")
if not tasks_file.exists():
    print("BLOCKED: tasks.json not found")
    sys.exit(1)

data = json.loads(tasks_file.read_text())

for task in data["tasks"]:
    if task["id"] == task_id:
        for subtask in task.get("subtasks", []):
            if subtask["skill"] == skill:
                subtask["gates"][gate_name] = True
                tasks_file.write_text(json.dumps(data, indent=2))
                print(f"Stamped {task_id}.{skill} / {gate_name}")
                sys.exit(0)
        print(f"BLOCKED: subtask with skill '{skill}' not found for task '{task_id}'")
        sys.exit(1)

print(f"BLOCKED: task '{task_id}' not found")
sys.exit(1)
