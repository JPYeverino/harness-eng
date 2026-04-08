"""
Called by the context skill after producing a context doc.
Usage: python write_context.py '<json>'

Writes memory/{task_id}_context.json.
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: write_context.py '<json>'")
    sys.exit(1)

try:
    data = json.loads(sys.argv[1])
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    sys.exit(1)

task_id = data.get("task_id")
if not task_id:
    print("Missing task_id in payload")
    sys.exit(1)

Path("memory").mkdir(exist_ok=True)
out = Path(f"memory/{task_id}_context.json")
out.write_text(json.dumps(data, indent=2))
print(f"Written: {out}")
