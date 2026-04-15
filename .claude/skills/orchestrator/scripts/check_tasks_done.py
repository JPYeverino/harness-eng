"""
Stop hook — blocks the agent from stopping if any task is not done.
Exit 0: all tasks complete, allow stop.
Exit 2: pending tasks found, inject continuation prompt.

When waiting_for_human.json exists, blocks in a poll loop until the
dashboard approves (deletes the sentinel + sets human_approved), then
injects a continuation prompt so the agent resumes without a manual re-run.
"""
import json
import sys
import time
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
        print(
            f"Waiting for human approval on: {', '.join(sorted(waiting_ids))}. "
            "Approve via the dashboard — this will resume automatically.",
            file=sys.stderr,
        )
        # Block until approval arrives. Three exit conditions:
        # 1. All tasks approved
        # 2. Any task rejected
        # 3. human_approved already set before sentinel was written (timing edge case)
        def _all_approved():
            return all(
                json.loads(Path(f"memory/{tid}_validation.json").read_text()).get("human_approved", False)
                for tid in waiting_ids
                if Path(f"memory/{tid}_validation.json").exists()
            )

        def _any_rejected():
            return any(
                json.loads(Path(f"memory/{tid}_validation.json").read_text()).get("human_rejected", False)
                for tid in waiting_ids
                if Path(f"memory/{tid}_validation.json").exists()
            )

        while sentinel.exists() and not _all_approved() and not _any_rejected():
            time.sleep(2)

        if _any_rejected():
            rejected_ids = [
                tid for tid in sorted(waiting_ids)
                if Path(f"memory/{tid}_validation.json").exists()
                and json.loads(Path(f"memory/{tid}_validation.json").read_text()).get("human_rejected", False)
            ]
            cmds = " && ".join(f"python cleanup.py {tid} --rejected" for tid in rejected_ids)
            msg = f"Task(s) rejected. Run exactly this and nothing else: {cmds}"
            print(msg)
            print(msg, file=sys.stderr)
            sys.exit(2)

        # Sentinel gone / all approved — inject continuation so the agent re-runs the validator gate.
        cmds = " && ".join(
            f"python .claude/skills/validator/scripts/gate_validation_passed.py {tid} && python .claude/skills/scripts/mark_done.py {tid} validator && python .claude/skills/scripts/mark_done.py {tid} && python cleanup.py {tid} --approved"
            for tid in sorted(waiting_ids)
        )
        msg = f"Human approved. Run exactly this and nothing else: {cmds}"
        print(msg)
        print(msg, file=sys.stderr)
        sys.exit(2)

ids = ", ".join(t["id"] for t in pending)
msg = f"Tasks not yet complete: {ids}. Run the orchestrator skill for each pending task."
print(msg)                   # stdout → injected as continuation prompt to Claude
print(msg, file=sys.stderr)  # stderr → shown in hook feedback UI
sys.exit(2)
