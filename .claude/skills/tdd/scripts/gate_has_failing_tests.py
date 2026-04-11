"""
Gate: checks that the agent already ran pytest and recorded a failing result.
Does NOT run pytest itself — forces the agent to observe the failure first.
Usage: python gate_has_failing_tests.py <test_file> <task_id>
Exits 0 if evidence of failure exists, 1 if blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

test_file = sys.argv[1] if len(sys.argv) > 1 else None
task_id = sys.argv[2] if len(sys.argv) > 2 else None

if not test_file or not task_id:
    print("Usage: gate_has_failing_tests.py <test_file> <task_id>")
    sys.exit(1)

if not Path(test_file).exists():
    print(f"BLOCKED: {test_file} does not exist — write tests first")
    sys.exit(1)

result_file = Path("memory/test_result.json")
if not result_file.exists():
    print("BLOCKED: memory/test_result.json not found — run tests and record the result first")
    sys.exit(1)

data = json.loads(result_file.read_text())
if data.get("passed") is not False:
    print("BLOCKED: test_result.json does not show a failure — tests must fail before writing implementation")
    sys.exit(1)

if data.get("test_file") != test_file:
    print(f"BLOCKED: test_result.json is for '{data.get('test_file')}', not '{test_file}' — re-run tests for the correct file")
    sys.exit(1)

subprocess.run(
    ["python", ".claude/skills/scripts/mark_gate.py", task_id, "tdd", "gate_has_failing_tests"],
    check=True,
)
print(f"OK: tests exist and fail — safe to implement")
sys.exit(0)
