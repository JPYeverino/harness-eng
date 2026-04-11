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

1. Read the spec from `spec.md`
2. Produce exactly one task covering the full implementation
3. Detect the stack from the spec. Set all stack fields present in the spec — at minimum `language`, `test_runner`, `test_command`. If the spec includes `e2e_runner`, `dev_url`, and `dev_command`, include those too.
4. Run: `python ${CLAUDE_SKILL_DIR}/scripts/write_tasks.py '<json>'`
   where `<json>` is:
   ```json
   {
     "tasks": [
       {
         "id": "task-1",
         "title": "...",
         "description": "...",
         "stack": {
           "language": "...",
           "test_runner": "...",
           "test_command": "...",
           "e2e_runner": "...",
           "dev_url": "...",
           "dev_command": "..."
         },
         "done": false,
         "dependsOn": []
       }
     ]
   }
   ```
   Omit `e2e_runner`, `dev_url`, and `dev_command` if the spec does not define them.
4. Confirm `tasks.json` was written
6. Run: `python ${CLAUDE_SKILL_DIR}/../scripts/scaffold_subtasks.py`
7. Run: `python ${CLAUDE_SKILL_DIR}/../scripts/mark_done.py task-1 planner`

Do not proceed to any other skill until `tasks.json` exists.
