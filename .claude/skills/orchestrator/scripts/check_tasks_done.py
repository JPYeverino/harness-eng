"""
Stop hook — blocks the agent from stopping if any task is not done.
Exit 0: all tasks complete, allow stop.
Exit 2: pending tasks found, inject continuation prompt.

Respects a waiting_for_human.json sentinel: if it exists and lists a
pending task id, Claude is intentionally blocked on a human gate — let
it stop quietly rather than re-injecting and looping.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdin.read()  # consume stdin (stop hook payload), not needed

tasks_file = Path("tasks.json")
if not tasks_file.exists():
    sys.exit(0)

tasks = json.loads(tasks_file.read_text())["tasks"]
pending = [t for t in tasks if not t.get("done")]

# log to run_log.jsonl so we can verify the hook fired
log_path = Path("memory/run_log.jsonl")
log_path.parent.mkdir(exist_ok=True)
entry = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "hook": "Stop",
    "pending": [t["id"] for t in pending],
    "all_done": len(pending) == 0,
}
with log_path.open("a") as f:
    f.write(json.dumps(entry) + "\n")

if not pending:
    sys.exit(0)

# Check if Claude is intentionally waiting for a human gate.
# The orchestrator writes this sentinel before stopping on a blocked gate.
sentinel = Path("memory/waiting_for_human.json")
if sentinel.exists():
    waiting = json.loads(sentinel.read_text())
    waiting_ids = set(waiting.get("task_ids", []))
    pending_ids = {t["id"] for t in pending}
    if pending_ids <= waiting_ids:
        # All pending tasks are blocked on human gates — let Claude stop.
        print(
            f"Waiting for human approval on: {', '.join(sorted(waiting_ids))}. "
            "Run the approve script, then re-run the orchestrator.",
            file=sys.stderr,
        )
        sys.exit(0)

ids = ", ".join(t["id"] for t in pending)
msg = f"Tasks not yet complete: {ids}. Run the orchestrator skill for each pending task."
print(msg)                   # stdout → injected as continuation prompt to Claude
print(msg, file=sys.stderr)  # stderr → shown in hook feedback UI
sys.exit(2)
