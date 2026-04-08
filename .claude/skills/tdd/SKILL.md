---
name: tdd
description: Run the full TDD cycle — failing tests, brute force, refactor. Called by the orchestrator — not user-facing.
allowed-tools: Read Write Bash
effort: high
user-invocable: false
---

# TDD Skill

Run the full TDD cycle: failing tests → brute force → refactor.

## Steps

### Gate: check context exists
`python ${CLAUDE_SKILL_DIR}/scripts/gate_context_exists.py <task_id>`
- Exit 1: stop, context is missing — run context skill first

### Step 1: Write failing tests
- Read `memory/{task_id}_context.json` for context
- Write test file
- Run pytest — confirm it fails
- Do NOT proceed to step 2 until tests fail

### Step 2: Write brute force implementation
Run the gate first:
`python ${CLAUDE_SKILL_DIR}/scripts/gate_has_failing_tests.py <test_file>`
- Exit 1: stop, tests are not failing — do not write implementation

- Write the simplest correct implementation (brute force)
- Run pytest — confirm tests pass

### Step 3: Refactor to optimal
Run the gate first:
`python ${CLAUDE_SKILL_DIR}/scripts/gate_has_implementation.py <impl_file> <test_file>`
- Exit 1: stop, implementation missing or tests not passing — do not refactor

- Refactor to the optimal solution
- Run pytest — confirm tests still pass

### Step 4: Write decisions
`python ${CLAUDE_SKILL_DIR}/scripts/write_decisions.py '<json>'`
where `<json>` is:
```json
{
  "task_id": "...",
  "test_file": "...",
  "impl_file": "...",
  "decisions": ["..."]
}
```

### Step 5: Mark done
`python ${CLAUDE_SKILL_DIR}/../scripts/mark_done.py <task_id> tdd`

## Rules
- Never skip a gate
- Never write implementation before tests fail
- Never refactor before implementation exists and tests pass
