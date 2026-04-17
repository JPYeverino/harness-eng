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
2. Break the spec into as many tasks as it naturally warrants. Rules:
   - Each task must be independently testable with a single clear deliverable
   - Tasks that touch the same file or share state should be one task
   - Tasks with no dependency on each other can be separate tasks
   - Use one task only if the spec is truly atomic
   - Assign sequential IDs: `task-1`, `task-2`, `task-3`, etc.
   - Set `dependsOn` to reflect real dependencies (e.g. `["task-1"]` if task-2 requires task-1's output)
2b. Boyscout pass — for each file listed in `## Deliverables` that already exists on disk:
   - Read the file
   - Note any of the following if present:
     * TODO or FIXME comments
     * Hardcoded values that should be config (magic strings, absolute paths)
     * Unused imports or dead code
     * Inconsistencies with the surrounding code (naming, style)
     * Anything that will complicate the upcoming change
   Write to `memory/planner_observations.json`:
   ```json
   {"files": {"dashboard.py": ["finding 1", "finding 2"], "dashboard.html": []}}
   ```
   Skip files that don't exist yet. If no existing files, write `{"files": {}}`.
   This is observation only — do not fix anything.

3. Detect the stack from the spec. Set all stack fields present in the spec — at minimum `language`, `test_runner`, `test_command`. If the spec includes `e2e_runner`, `dev_url`, and `dev_command`, include those too. All tasks share the same stack.
4. Run: `python ${CLAUDE_SKILL_DIR}/scripts/write_tasks.py '<json>'`
   where `<json>` is an array of all tasks:
   ```json
   {
     "tasks": [
       {
         "id": "task-1",
         "title": "...",
         "description": "...",
         "stack": { "language": "...", "test_runner": "...", "test_command": "..." },
         "done": false,
         "dependsOn": []
       },
       {
         "id": "task-2",
         "title": "...",
         "description": "...",
         "stack": { "language": "...", "test_runner": "...", "test_command": "..." },
         "done": false,
         "dependsOn": ["task-1"]
       }
     ]
   }
   ```
   Omit `e2e_runner`, `dev_url`, and `dev_command` from stack if the spec does not define them.
5. Confirm `tasks.json` was written
6. Run: `python ${CLAUDE_SKILL_DIR}/../scripts/scaffold_subtasks.py`
7. For every task ID in the tasks array, run:
   `python ${CLAUDE_SKILL_DIR}/../scripts/mark_done.py <task-id> planner`

Do not proceed to any other skill until `tasks.json` exists.
