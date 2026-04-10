---
name: planner
description: Break a spec into tasks and write tasks.json. Called by the orchestrator — not user-facing.
allowed-tools: Read Bash
effort: low
user-invocable: false
---

# Planner Skill

Break the spec into tasks and write them to disk.

## Steps

1. Read the spec from `spec.py`
2. Produce exactly one task covering the full implementation
3. Run: `python ${CLAUDE_SKILL_DIR}/scripts/write_tasks.py '<json>'`
   where `<json>` is:
   ```json
   {
     "tasks": [
       { "id": "task-1", "title": "...", "description": "...", "done": false, "dependsOn": [] }
     ]
   }
   ```
4. Confirm `tasks.json` was written
5. Run: `python ${CLAUDE_SKILL_DIR}/../scripts/scaffold_subtasks.py`
6. Run: `python ${CLAUDE_SKILL_DIR}/../scripts/mark_done.py task-1 planner`

Do not proceed to any other skill until `tasks.json` exists.
