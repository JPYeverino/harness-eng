"""
Gate: implementation file must exist and tests must pass before refactoring.
Usage: python gate_has_implementation.py <impl_file> <test_file>
Exits 0 if safe to refactor, 1 if blocked.
"""
import sys
import subprocess
from pathlib import Path

impl_file = sys.argv[1] if len(sys.argv) > 1 else None
test_file = sys.argv[2] if len(sys.argv) > 2 else None

if not impl_file or not test_file:
    print("Usage: gate_has_implementation.py <impl_file> <test_file>")
    sys.exit(1)

if not Path(impl_file).exists():
    print(f"BLOCKED: {impl_file} does not exist — write implementation first")
    sys.exit(1)

result = subprocess.run(["pytest", test_file, "--tb=no", "-q"], capture_output=True)
if result.returncode != 0:
    print("BLOCKED: tests are not passing — fix implementation before refactoring")
    sys.exit(1)

print(f"OK: implementation exists and tests pass — safe to refactor")
sys.exit(0)
