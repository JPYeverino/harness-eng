"""
Appends a new entry to memory/{task_id}_decisions.json.
Usage: python write_decisions.py '<json>'
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: write_decisions.py '<json>'")
    sys.exit(1)

try:
    new_entry = json.loads(sys.argv[1])
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    sys.exit(1)

task_id = new_entry.get("task_id")
if not task_id:
    print("Missing task_id in payload")
    sys.exit(1)

Path("memory").mkdir(exist_ok=True)
out = Path(f"memory/{task_id}_decisions.json")

existing = json.loads(out.read_text()) if out.exists() else {"task_id": task_id, "entries": []}
existing.setdefault("entries", [])
existing["entries"].append(new_entry)

out.write_text(json.dumps(existing, indent=2))
print(f"Appended entry to {out} ({len(existing['entries'])} total)")
