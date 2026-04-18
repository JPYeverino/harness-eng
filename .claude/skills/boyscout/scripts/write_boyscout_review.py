"""
Writes memory/boyscout_review.json.
Usage: python write_boyscout_review.py '<json>'
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

REQUIRED_KEYS = {"status", "lore_checked", "files_scanned", "context_generated", "opportunities"}
VALID_STATUSES = {"needs_review", "proceed"}

if len(sys.argv) < 2:
    print("Usage: write_boyscout_review.py '<json>'")
    sys.exit(1)

try:
    data = json.loads(sys.argv[1])
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    sys.exit(1)

missing = REQUIRED_KEYS - set(data.keys())
if missing:
    print(f"Missing required keys: {', '.join(sorted(missing))}")
    sys.exit(1)

if data["status"] not in VALID_STATUSES:
    print(f"Invalid status '{data['status']}' — must be one of: {', '.join(VALID_STATUSES)}")
    sys.exit(1)

if not isinstance(data["files_scanned"], list):
    print("files_scanned must be a list")
    sys.exit(1)

if not isinstance(data["context_generated"], list):
    print("context_generated must be a list")
    sys.exit(1)

if not isinstance(data["opportunities"], dict):
    print("opportunities must be an object")
    sys.exit(1)

Path("memory").mkdir(exist_ok=True)
Path("memory/boyscout_review.json").write_text(json.dumps(data, indent=2))
print(f"Written: memory/boyscout_review.json (status={data['status']})")
