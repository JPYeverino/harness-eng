---
name: orchestrator
description: Run the full TDD harness — planner, context, tdd, validator — in order with gates enforcing each step. Use when given a spec to implement.
allowed-tools: Read Write Bash Glob
effort: high
hooks:
  Stop:
    - matcher: ".*"
      hooks:
        - type: command
          command: "python .claude/skills/orchestrator/scripts/check_tasks_done.py"
  PostToolUse:
    - matcher: ".*"
      hooks:
        - type: command
          command: "python .claude/skills/orchestrator/scripts/log_event.py"
---

# Orchestrator

Run these skills in order. Each skill has gates — if a gate fails, stop and report why.

## Step 0: Validate spec

Run: `python check_spec.py`
- Exit 1: spec is invalid — show the findings to the user, do not proceed
- Exit 0: spec is valid, continue

## Step 0b: Boyscout

Load and follow `.claude/skills/boyscout/SKILL.md`

After boyscout completes, run: `python .claude/skills/boyscout/scripts/gate_boyscout_clear.py`
- Exit 1: review pending — show instructions to the user, do not proceed
- Exit 0: approved, continue to planner

## Order

1. Load and follow `.claude/skills/planner/SKILL.md`
2. Load and follow `.claude/skills/context/SKILL.md`
3. Load and follow `.claude/skills/tdd/SKILL.md`
4. Load and follow `.claude/skills/validator/SKILL.md`

## Rules

- Never skip a skill
- Never skip a gate inside a skill
- Gates are scripts — if they exit 1, you are blocked, do not proceed
- Read `tasks.json` before starting each skill — check the matching subtask's `done` flag
- If `subtasks[skill].done == true`, skip that skill and move to the next
- The gate scripts handle SKIP automatically — if they exit 0 with SKIP, stop and move on
