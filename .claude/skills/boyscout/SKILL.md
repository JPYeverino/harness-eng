---
name: boyscout
description: Assess current state of deliverable files before planning starts. Generates missing docs, surfaces smells, blocks for human review. Called by the orchestrator — not user-facing.
allowed-tools: Read Write Bash
effort: medium
user-invocable: false
---

# Boyscout Skill

Assess what is already on disk before the planner writes tasks.json.
Never fix anything. Observe, document, surface — then wait for human approval.

## Steps

### Step 1: Load existing state

Read in this order — this is your memory of prior runs:

1. `docs/lore.md` — if it exists, read it entirely. Note every filename and
   smell mentioned. You will NOT re-flag anything already in lore.
   Set `lore_checked: true` in your output. If file does not exist, set `lore_checked: false`.
2. `docs/business-flows/` — read any file present. This is intent.
3. `docs/diagrams/` — read any file present. This is prior structural understanding.

### Step 2: Read spec.md

Extract the list of filenames from `## Deliverables`.
For each filename, check if it exists on disk (`Path(filename).exists()`).
Only files that exist on disk are in scope for this pass.

### Step 3: For each existing deliverable file

**3a. Check context coverage:**
A file has context if ANY of these is true:
- `docs/diagrams/{filename}.md` exists
- `docs/business-flows/` contains a file that mentions this filename
- `docs/lore.md` mentions this filename

**3b. If no context exists:**
- Read the file
- Generate `docs/diagrams/{filename}.md` with:
  - A `## What it does` section (plain language, derived from code — not opinion)
  - A `## Flow` section with a Mermaid diagram of the main logic or steps
  - A `## Dependencies` section listing what it reads/writes/calls
- Add this filename to `context_generated` in your output

**3b. If context exists:**
- Read the file
- Read its `docs/diagrams/{filename}.md`
- Note any smells NOT already in `docs/lore.md`:
  * TODO or FIXME comments
  * Hardcoded values (magic strings, absolute paths)
  * Unused imports or dead code
  * Style or naming inconsistencies
  * Anything that will complicate the upcoming change
- Add findings to `opportunities` in your output

### Step 4: Expand spec.md if context was generated

If any files had no context (step 3b generated new docs), append to `spec.md`:

```
## Context gaps filled by boyscout

The following files had no prior documentation. Diagrams were generated
and require human review before planning proceeds:

- `filename.py` — see docs/diagrams/filename.py.md
```

### Step 5: Write memory/boyscout_review.json

Run: `python ${CLAUDE_SKILL_DIR}/scripts/write_boyscout_review.py '<json>'`

```json
{
  "status": "needs_review",
  "lore_checked": true,
  "files_scanned": ["dashboard.py", "dashboard.html"],
  "context_generated": ["dashboard.py"],
  "opportunities": {
    "dashboard.html": ["line 18: inline style conflicts with stylesheet"]
  }
}
```

Set `status: "proceed"` only when: all files had existing context AND no smells found.
Otherwise always `status: "needs_review"`.

### Step 6: Gate — wait for human approval

Run: `python ${CLAUDE_SKILL_DIR}/scripts/gate_boyscout_clear.py`
- Exit 1: blocked — show the printed instructions to the user, do not proceed
- Exit 0: approved, continue to planner

## Rules
- Never modify any deliverable file — observation only
- Never re-flag smells already in docs/lore.md
- Always set lore_checked in output — even if lore.md does not exist
- Always list every scanned file in files_scanned
- Mermaid diagrams only — no prose-only diagrams
