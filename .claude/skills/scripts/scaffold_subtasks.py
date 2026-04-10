"""
Expands tasks in tasks.json with the standard harness subtask pipeline.
Run after write_tasks.py — each task gets planner/context/tdd/validator subtasks
with dependsOn chains and gate stamp maps.
Usage: python scaffold_subtasks.py
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

PIPELINE = [
    {
        "skill": "planner",
        "dependsOn_prev": False,
        "gates": {},
    },
    {
        "skill": "context",
        "dependsOn_prev": True,
        "gates": {"gate_task_exists": False},
    },
    {
        "skill": "tdd",
        "dependsOn_prev": True,
        "gates": {
            "gate_context_exists": False,
            "gate_has_failing_tests": False,
            "gate_has_implementation": False,
        },
    },
    {
        "skill": "validator",
        "dependsOn_prev": True,
        "gates": {
            "gate_tdd_done": False,
            "gate_validation_passed": False,
        },
    },
]

tasks_file = Path("tasks.json")
if not tasks_file.exists():
    print("BLOCKED: tasks.json not found — run write_tasks.py first")
    sys.exit(1)

data = json.loads(tasks_file.read_text())

for task in data["tasks"]:
    task_id = task["id"]
    subtasks = []
    prev_id = None

    for step in PIPELINE:
        subtask_id = f"{task_id}.{step['skill']}"
        depends_on = [prev_id] if step["dependsOn_prev"] and prev_id else []
        subtasks.append({
            "id": subtask_id,
            "skill": step["skill"],
            "done": False,
            "dependsOn": depends_on,
            "gates": dict(step["gates"]),
        })
        prev_id = subtask_id

    task["subtasks"] = subtasks
    task.pop("completed", None)  # remove old schema if present

tasks_file.write_text(json.dumps(data, indent=2))
print(f"Scaffolded subtasks for {len(data['tasks'])} task(s)")
