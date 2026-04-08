"""
Gate: a test file must exist AND pytest must fail before writing implementation.
Usage: python gate_has_failing_tests.py <test_file>
Exits 0 if tests exist and fail (safe to implement), 1 if blocked.
"""
import sys
import subprocess
from pathlib import Path

test_file = sys.argv[1] if len(sys.argv) > 1 else None
if not test_file:
    print("Usage: gate_has_failing_tests.py <test_file>")
    sys.exit(1)

if not Path(test_file).exists():
    print(f"BLOCKED: {test_file} does not exist — write tests first")
    sys.exit(1)

result = subprocess.run(["pytest", test_file, "--tb=no", "-q"], capture_output=True)
if result.returncode == 0:
    print("BLOCKED: tests are passing — implementation already exists or tests are wrong")
    sys.exit(1)

print(f"OK: tests exist and fail — safe to implement")
sys.exit(0)
