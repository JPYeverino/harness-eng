#!/usr/bin/env python3
"""PostToolUse hook — appends a timestamped entry to memory/run_log.jsonl."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

data = json.loads(sys.stdin.read())

entry = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "tool": data.get("tool_name"),
    "input": data.get("tool_input"),
    "response_snippet": str(data.get("tool_response", ""))[:200],
}

log_path = Path("memory/run_log.jsonl")
log_path.parent.mkdir(exist_ok=True)
with log_path.open("a") as f:
    f.write(json.dumps(entry) + "\n")
