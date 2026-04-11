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
- Read `tasks.json` and find the task's `stack.test_command`
- Write test file
- Run the test command — observe the failure output, understand why it fails
- Record the result: `python ${CLAUDE_SKILL_DIR}/scripts/record_test_result.py <test_file> false`
- Do NOT proceed to step 2 until tests fail

### Step 2: Write brute force implementation
Run the gate first:
`python ${CLAUDE_SKILL_DIR}/scripts/gate_has_failing_tests.py <test_file> <task_id>`
- Exit 1: stop — you have not recorded a failing test result yet

- Write the simplest correct implementation (brute force)
- Run the test command — observe that tests pass
- Record the result: `python ${CLAUDE_SKILL_DIR}/scripts/record_test_result.py <test_file> true`

### Step 3: Refactor to optimal
Run the gate first:
`python ${CLAUDE_SKILL_DIR}/scripts/gate_has_implementation.py <impl_file> <test_file> <task_id>`
- Exit 1: stop — you have not recorded a passing test result yet

- Refactor to the optimal solution
- Run the test command — confirm tests still pass
- Record the result: `python ${CLAUDE_SKILL_DIR}/scripts/record_test_result.py <test_file> true`

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
