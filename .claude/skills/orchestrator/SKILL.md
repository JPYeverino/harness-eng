---
name: orchestrator
description: Run the full TDD harness — planner, context, tdd — in order with gates enforcing each step. Use when given a spec to implement.
allowed-tools: Read Write Bash Glob
effort: high
---

# Orchestrator

Run these skills in order. Each skill has gates — if a gate fails, stop and report why.

## Order

1. Load and follow `.claude/skills/planner/SKILL.md`
2. Load and follow `.claude/skills/context/SKILL.md`
3. Load and follow `.claude/skills/tdd/SKILL.md`

## Rules

- Never skip a skill
- Never skip a gate inside a skill
- Gates are scripts — if they exit 1, you are blocked, do not proceed
- Read `memory/` before starting each skill to check for prior work
- If a skill's work is already done (completed flag in tasks.json), skip it and move to the next
