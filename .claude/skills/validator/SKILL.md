---
name: validator
description: Cold-review TDD output — checks tests against spec, impl against spec constraints, and runs e2e checks via agent-browser if stack.dev_url is set. Called by the orchestrator after tdd — not user-facing.
allowed-tools: Read Write Bash
effort: medium
user-invocable: false
---

# Validator Skill

You are a fresh agent with no knowledge of how the tests or implementation were written.
Your job is to independently verify that the TDD output satisfies the original spec.

## Inputs — read these before anything else

1. `spec.md` — the original problem spec
2. `tasks.json` — to get `stack` for this task (test_command, e2e_runner, dev_url, dev_command)
3. `memory/{task_id}_context.json` — the planned approach
4. `memory/{task_id}_decisions.json` — to get `test_file` and `impl_file`
5. The test file and the implementation file (paths from decisions above)

## Steps

### Gate: check tdd is done
`python .claude/skills/validator/scripts/gate_tdd_done.py <task_id>`
- Exit 1: stop — TDD skill has not completed, cannot validate
- Exit 0 with SKIP: validator already done, stop

### Step 1: Read all inputs
- Read `spec.md` in full
- Read `tasks.json` — find this task by `task_id`, extract `stack`
- Read `memory/{task_id}_context.json`
- Read `memory/{task_id}_decisions.json` to find `test_file` and `impl_file`
- Read the test file and the implementation file

### Step 2: Evaluate independently — run all four unit checks

For each check, produce `passed: true/false` and a `notes` string:

**spec_coverage**: Do the tests cover every constraint and example in the spec?
- Is each constraint exercised by at least one test case?
- Does the example input/output from the spec appear as a test?
- Are all required deliverables from the spec present on disk?

**constraint_compliance**: Does the implementation respect every spec constraint?
- Does every file listed in the spec's Deliverables section exist?
- Are there constraints the impl must enforce or rely on?

**test_validity**: Are the tests correct — do they test what they claim?
- Are any test inputs ambiguous?
- Does any test assert a wrong expected value?

**impl_correctness**: Does the implementation produce correct output for all test cases?
- Trace through the impl mentally for at least the example case
- Does the impl handle the edge cases the tests exercise?

### Step 3: E2E validation (skip if `stack.e2e_runner` is absent)

Read `stack.dev_url` and `stack.dev_command` from `tasks.json`.

**Start the dev server if not already running:**
```bash
curl -s {dev_url} > /dev/null 2>&1 || ({dev_command} > /tmp/dev_server.log 2>&1 & sleep 3)
```

**Observe the running app with agent-browser:**
```bash
agent-browser open {dev_url}
agent-browser snapshot
agent-browser screenshot memory/{task_id}_screenshot.png
agent-browser close
```

Read the snapshot output. Check each item from the spec's Deliverables section:
- Does the root URL load without error (not 404, not 500)?
- Are the panels described in the spec present in the accessibility tree?
- Does the HITL Approve button appear for tasks with `human_approved: false`?

Produce an `e2e` check: `passed: true/false` and `notes` describing what was found.
Add any e2e failures to `findings`.

### Step 4: Write findings
- `findings` is a list of strings describing any problem found — empty if all passed
- `passed` (top-level) is `true` only if ALL checks passed (unit + e2e if run)

### Step 5: Record validation
`python .claude/skills/validator/scripts/write_validation.py '<json>'`

where `<json>` is:
```json
{
  "task_id": "...",
  "passed": true,
  "checks": {
    "spec_coverage":         { "passed": true, "notes": "..." },
    "constraint_compliance": { "passed": true, "notes": "..." },
    "test_validity":         { "passed": true, "notes": "..." },
    "impl_correctness":      { "passed": true, "notes": "..." },
    "e2e":                   { "passed": true, "notes": "..." }
  },
  "findings": []
}
```

The `e2e` key is omitted if `stack.e2e_runner` is absent.

If the script exits 1 with "already approved" — the validation was already written and approved by a human. Proceed directly to the gate.

### Step 5: Gate — wait for human approval
`python .claude/skills/validator/scripts/gate_validation_passed.py <task_id>`
- Exit 1: blocked — follow the printed instructions to approve
- Exit 0: approved, proceed

### Step 6: Mark done
`python .claude/skills/scripts/mark_done.py <task_id> validator`

## Rules
- Do NOT run pytest — you are a cold reviewer, not a runner
- Do NOT look at git history, prior sessions, or any memory file not listed above
- Do NOT call `approve_validation.py` — that script is for humans only
- If any check fails, set top-level `passed: false` and populate `findings`
- agent-browser is observation only — do not click Approve or submit forms
- If the dev server fails to start, mark e2e as failed with the error in notes
