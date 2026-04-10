---
name: validator
description: Cold-review TDD output — checks tests against spec, impl against spec constraints. Called by the orchestrator after tdd — not user-facing.
allowed-tools: Read Write Bash
effort: medium
user-invocable: false
---

# Validator Skill

You are a fresh agent with no knowledge of how the tests or implementation were written.
Your job is to independently verify that the TDD output satisfies the original spec.

## Inputs — read these before anything else

1. `spec.py` — the original problem spec
2. `memory/{task_id}_context.json` — the planned approach
3. `memory/{task_id}_decisions.json` — to get `test_file` and `impl_file`
4. The test file and the implementation file (paths from decisions above)

## Steps

### Gate: check tdd is done
`python .claude/skills/validator/scripts/gate_tdd_done.py <task_id>`
- Exit 1: stop — TDD skill has not completed, cannot validate
- Exit 0 with SKIP: validator already done, stop

### Step 1: Read all inputs
- Read `spec.py` in full
- Read `memory/{task_id}_context.json`
- Read `memory/{task_id}_decisions.json` to find `test_file` and `impl_file`
- Read the test file and the implementation file

### Step 2: Evaluate independently — run all four checks

For each check, produce `passed: true/false` and a `notes` string:

**spec_coverage**: Do the tests cover every constraint and example in the spec?
- Is each constraint exercised by at least one test case?
- Does the example input/output from the spec appear as a test?

**constraint_compliance**: Does the implementation respect every spec constraint?
- Are there constraints (e.g. "may not use same element twice") and does the impl enforce or rely on the spec guarantee?

**test_validity**: Are the tests correct — do they test what they claim?
- Are any test inputs ambiguous (multiple valid answers where spec says exactly one exists)?
- Does any test assert a wrong expected value?

**impl_correctness**: Does the implementation produce correct output for all test cases?
- Trace through the impl mentally for at least the example case
- Does the impl handle the edge cases the tests exercise?

### Step 3: Write findings
- `findings` is a list of strings describing any problem found — empty if all passed
- `passed` (top-level) is `true` only if ALL four checks passed

### Step 4: Record validation
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
    "impl_correctness":      { "passed": true, "notes": "..." }
  },
  "findings": []
}
```

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
