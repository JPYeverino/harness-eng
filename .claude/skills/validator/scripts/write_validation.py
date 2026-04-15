"""
Called by the validator agent after completing its review.
Usage: python write_validation.py '<json>'

Writes memory/{task_id}_validation.json with human_approved: false.
Guards against overwriting an already-approved validation.
Exits 0 on success, 1 on failure.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: write_validation.py '<json>'")
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

required_checks = {"spec_coverage", "constraint_compliance", "test_validity", "impl_correctness"}
checks = data.get("checks", {})
missing = required_checks - set(checks.keys())
if missing:
    print(f"Missing required checks: {missing}")
    sys.exit(1)

out = Path(f"memory/{task_id}_validation.json")
if out.exists():
    existing = json.loads(out.read_text())
    if existing.get("human_approved"):
        print(f"BLOCKED: {out} already exists and is human-approved — do not overwrite. Proceed to gate_validation_passed.py.")
        sys.exit(1)

Path("memory").mkdir(exist_ok=True)
record = {
    "task_id": task_id,
    "passed": bool(data.get("passed")),
    "summary": data.get("summary") or "",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "checks": checks,
    "findings": data.get("findings", []),
    "human_approved": False,
}
out.write_text(json.dumps(record, indent=2))
print(f"Written: {out}")
