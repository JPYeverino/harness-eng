"""
Called by the agent after running pytest to record the result in memory.
Usage: python record_pytest_result.py <test_file> <passed: true|false>
"""
import sys
import json
from pathlib import Path

test_file = sys.argv[1] if len(sys.argv) > 1 else None
passed_arg = sys.argv[2].lower() if len(sys.argv) > 2 else None

if not test_file or passed_arg not in ("true", "false"):
    print("Usage: record_pytest_result.py <test_file> <true|false>")
    sys.exit(1)

result = {"test_file": test_file, "passed": passed_arg == "true"}
Path("memory").mkdir(exist_ok=True)
Path("memory/pytest_result.json").write_text(json.dumps(result, indent=2))
print(f"Recorded: {test_file} passed={result['passed']}")
