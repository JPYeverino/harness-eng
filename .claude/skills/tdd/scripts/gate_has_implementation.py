"""
Gate: checks that the agent already ran pytest and recorded a passing result.
Does NOT run pytest itself — forces the agent to observe the green state first.
Usage: python gate_has_implementation.py <impl_file> <test_file> <task_id>
Exits 0 if safe to refactor, 1 if blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

impl_file = sys.argv[1] if len(sys.argv) > 1 else None
test_file = sys.argv[2] if len(sys.argv) > 2 else None
task_id = sys.argv[3] if len(sys.argv) > 3 else None

if not impl_file or not test_file or not task_id:
    print("Usage: gate_has_implementation.py <impl_file> <test_file> <task_id>")
    sys.exit(1)

if not Path(impl_file).exists():
    print(f"BLOCKED: {impl_file} does not exist — write implementation first")
    sys.exit(1)

result_file = Path("memory/pytest_result.json")
if not result_file.exists():
    print("BLOCKED: memory/pytest_result.json not found — run pytest and record the result first")
    sys.exit(1)

data = json.loads(result_file.read_text())
if data.get("passed") is not True:
    print("BLOCKED: pytest_result.json does not show passing tests — fix implementation before refactoring")
    sys.exit(1)

if data.get("test_file") != test_file:
    print(f"BLOCKED: pytest_result.json is for '{data.get('test_file')}', not '{test_file}' — re-run pytest for the correct file")
    sys.exit(1)

subprocess.run(
    ["python", ".claude/skills/scripts/mark_gate.py", task_id, "tdd", "gate_has_implementation"],
    check=True,
)
print(f"OK: implementation exists and tests pass — safe to refactor")
sys.exit(0)
