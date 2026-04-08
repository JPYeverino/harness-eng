"""
Called by the planner skill after deciding on tasks.
Usage: python write_tasks.py '<json>'

Writes tasks.json to the project root with dependsOn chains.
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: write_tasks.py '<json>'")
    sys.exit(1)

try:
    tasks = json.loads(sys.argv[1])
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    sys.exit(1)

Path("tasks.json").write_text(json.dumps(tasks, indent=2))
print(f"tasks.json written with {len(tasks['tasks'])} task(s)")
