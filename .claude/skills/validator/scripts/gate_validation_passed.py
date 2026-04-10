"""
Gate: validation must exist, passed must be true, and human must have approved.
Usage: python gate_validation_passed.py <task_id>
Exits 0 if approved, 1 if blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: gate_validation_passed.py <task_id>")
    sys.exit(1)

val_file = Path(f"memory/{task_id}_validation.json")
if not val_file.exists():
    print(f"BLOCKED: memory/{task_id}_validation.json not found — run validator skill first")
    sys.exit(1)

data = json.loads(val_file.read_text())

if not data.get("passed"):
    print(f"BLOCKED: validator did not pass for {task_id}. Findings:")
    for f in data.get("findings", []):
        print(f"  - {f}")
    print("Fix the issues and re-run the validator skill.")
    sys.exit(1)

if not data.get("human_approved"):
    print(f"BLOCKED: human approval required for {task_id}.")
    print(f"  1. Read memory/{task_id}_validation.json and review the findings")
    print(f"  2. If satisfied, run:")
    print(f"     python .claude/skills/validator/scripts/approve_validation.py {task_id}")
    print(f"  3. Re-run the orchestrator to continue")
    sys.exit(1)

subprocess.run(
    ["python", ".claude/skills/scripts/mark_gate.py", task_id, "validator", "gate_validation_passed"],
    check=True,
)
print(f"OK: validation passed and human approved for {task_id}")
sys.exit(0)
