---
name: docs-updater
description: Updates docs/diagrams/ and docs/lore.md after an approved run. Rewrites diagrams for changed files, removes resolved lore entries. Called by the orchestrator after all tasks are approved — not user-facing.
allowed-tools: Read Write Bash
effort: medium
user-invocable: false
---

# Docs Updater Skill

Runs after all tasks are approved. Updates docs/ to reflect what was just built.
Never removes lore without evidence the smell is gone. Never overwrites a diagram
that hasn't changed.

## Inputs — read these before anything else

1. `tasks.json` — find all completed tasks
2. `memory/{task_id}_decisions.json` — get `impl_file` for each completed task
3. The current content of each `impl_file`
4. `docs/diagrams/{impl_filename}.md` — the prior diagram, if it exists
5. `docs/lore.md` — existing lore entries, if it exists

## Steps

### Step 1: Collect changed files

For each completed task in `tasks.json`:
- Read `memory/{task_id}_decisions.json`
- Extract `impl_file`
- Read the current content of `impl_file`

### Step 2: Update diagrams

For each `impl_file`:
- Read `docs/diagrams/{impl_filename}.md` if it exists (prior diagram)
- Read the current file content
- Compare: has the structure, logic, or dependencies changed from what the
  prior diagram describes?
  - **No meaningful change** → skip, leave diagram as-is
  - **Changed** → rewrite `docs/diagrams/{impl_filename}.md` with:
    - `## What it does` — plain language, derived from code
    - `## Flow` — Mermaid diagram of main logic or steps
    - `## Dependencies` — what it reads, writes, calls
    - `## Changed this run` — one line describing what was added or modified

### Step 3: Update lore

Read `docs/lore.md`. For each entry:
- Does the smell it describes still exist in the current code?
  - **Still present** → leave the entry unchanged
  - **Fixed in this run** → remove the entry, it is no longer true

If any entries were removed, rewrite `docs/lore.md` with a note at the top:
```
<!-- Last updated: {date} — {n} resolved entries removed -->
```

### Step 4: Done

No gates, no approval needed — this is documentation, not code.
Print a summary of what was updated.
