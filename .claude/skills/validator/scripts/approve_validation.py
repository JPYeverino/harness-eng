"""
Human-run script to approve a completed validation.
Usage: python .claude/skills/validator/scripts/approve_validation.py <task_id>

Sets human_approved: true in memory/{task_id}_validation.json.
Refuses to approve if the validator found failures — fix issues first.
Exits 0 on success, 1 on failure.
"""
import json
import sys
from pathlib import Path

task_id = sys.argv[1] if len(sys.argv) > 1 else None
if not task_id:
    print("Usage: approve_validation.py <task_id>")
    sys.exit(1)

val_file = Path(f"memory/{task_id}_validation.json")
if not val_file.exists():
    print(f"BLOCKED: {val_file} does not exist — run the validator skill first")
    sys.exit(1)

data = json.loads(val_file.read_text())

if not data.get("passed"):
    print(f"Cannot approve: validator found failures for {task_id}.")
    print("Findings:")
    for f in data.get("findings", []):
        print(f"  - {f}")
    print("\nFix the issues and re-run the validator skill before approving.")
    print("(To override, edit human_approved directly in the JSON file.)")
    sys.exit(1)

data["human_approved"] = True
val_file.write_text(json.dumps(data, indent=2))
print(f"Approved: {val_file}")

# Clean up the waiting_for_human sentinel so the Stop hook re-arms
sentinel = Path("memory/waiting_for_human.json")
if sentinel.exists():
    sentinel_data = json.loads(sentinel.read_text())
    task_ids = set(sentinel_data.get("task_ids", []))
    task_ids.discard(task_id)
    if task_ids:
        sentinel_data["task_ids"] = sorted(task_ids)
        sentinel.write_text(json.dumps(sentinel_data, indent=2))
    else:
        sentinel.unlink()
    print("Stop hook re-armed.")

print("Re-run the orchestrator to continue.")
