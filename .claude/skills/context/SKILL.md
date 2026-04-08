---
name: context
description: Produce a context document per task covering what to build and how. Called by the orchestrator — not user-facing.
allowed-tools: Read Bash
effort: low
user-invocable: false
---

# Context Skill

Produce a context document for each task and write it to memory.

## Steps

1. Read `tasks.json`
2. For each task, run the gate:
   `python ${CLAUDE_SKILL_DIR}/scripts/gate_task_exists.py <task_id>`
   - If exit 1: stop, report the block reason
   - If exit 0 with SKIP: context already exists, move to next task
3. Produce a context document covering:
   - `what`: what needs to be built
   - `approach`: brute force first, then optimal — explain the tradeoff
   - `notes`: anything the TDD agent should know
4. Run: `python ${CLAUDE_SKILL_DIR}/scripts/write_context.py '<json>'`
   where `<json>` is:
   ```json
   { "task_id": "...", "what": "...", "approach": "...", "notes": "..." }
   ```
5. Confirm the file was written to `memory/{task_id}_context.json`
6. Run: `python ${CLAUDE_SKILL_DIR}/../scripts/mark_done.py <task_id> context`

Do not produce implementation or tests — context only.
