# Spec: Run summary and run-level approval

## Overview

Three improvements that together make the dashboard readable by a non-technical user:

1. **Validator writes a plain-language summary** — after completing its checks, the validator
   writes a `summary` field in plain English describing what was built and the quality outcome.
   Written for the person who requested the output, not the engineer who built it.

2. **Run-level summary API** — a new `GET /api/run` endpoint aggregates all task summaries,
   total check counts, and approval state into a single response the dashboard can consume.

3. **Dashboard shows summary + run-level approval** — the result hero shows the plain-language
   summary prominently instead of raw file content. One Approve button and one Reject button
   act on the whole run (all tasks), not individual tasks.

## Reference files to read before starting

- `.claude/skills/validator/SKILL.md` — validator instructions (add summary step)
- `.claude/skills/validator/scripts/write_validation.py` — add `summary` field support
- `dashboard.py` — add `GET /api/run` endpoint
- `dashboard.html` — update result hero to show summary + run-level buttons

## Stack

- language: Python
- test_runner: pytest
- test_command: pytest -v

## Deliverables

- `.claude/skills/validator/scripts/write_validation.py` — accepts and writes `summary` field
- `.claude/skills/validator/SKILL.md` — updated with summary writing instructions
- `dashboard.py` — new `GET /api/run` endpoint
- `dashboard.html` — updated result hero

## Scope

### What gets unit-tested (pytest)

**`write_validation.py`:**
- Accepts a `summary` field in the JSON payload and writes it to validation file
- `summary` is optional — missing summary writes empty string, does not fail
- Existing approved validation still blocks overwrite (unchanged behaviour)

**`GET /api/run`:**
- Returns 404 when `tasks.json` has no tasks
- Returns `awaiting_approval: false` when no tasks have `gate_tdd_done` stamped
- Returns `awaiting_approval: true` when at least one task has `gate_tdd_done` stamped and `human_approved: false` and `human_rejected` is not true
- Returns correct `total_checks` (sum of all check counts across all task validations)
- Returns correct `checks_passed` (sum of passed checks across all task validations)
- Returns `all_approved: true` when all tasks have `human_approved: true`
- Returns `summaries` as a list of non-empty strings when validation files have summaries
- Returns `task_ids` list of all task IDs

**`dashboard.html`:**
- Write `test_dashboard_html_run.py` with smoke tests that read the file and assert:
  - `id="run-summary"` exists
  - `/api/run` appears in the JS
  - `id="run-approve-btn"` exists
  - `id="run-reject-btn"` exists
  - These tests must fail before `dashboard.html` is updated — write them first.

### What is out of scope for unit tests (but still required)

- `validator/SKILL.md` — verified by reading the file and confirming the summary
  writing instruction is present

## Implementation details

### write_validation.py — add summary field

Accept an optional `summary` string in the payload. Write it to the JSON record:

```python
record = {
    "task_id": task_id,
    "passed": bool(data.get("passed")),
    "summary": data.get("summary", ""),
    "timestamp": ...,
    "checks": checks,
    "findings": data.get("findings", []),
    "human_approved": False,
}
```

### validator/SKILL.md — summary writing instruction

Add a **Step 3: Write a plain-language summary** between the checks and the record step:

```
Write a `summary` string: 1–2 sentences in plain English describing what was built
and the quality outcome. Write for the person who requested the output — not a
technical audience. Do not mention task IDs, gate names, or internal tooling.

Good examples:
- "Five LinkedIn posts written in your brand voice, all under 200 words with a
  clear call-to-action in each."
- "Reject button added to the dashboard so you can send work back for revision,
  and the approval flow now handles multiple tasks correctly."

Bad examples (too technical):
- "gate_validation_passed stamped for task-2"
- "4/4 checks passed: spec_coverage, constraint_compliance, test_validity, impl_correctness"
```

### GET /api/run — new endpoint in dashboard.py

Reads `tasks.json` and all `memory/{task_id}_validation.json` files. Returns:

```json
{
  "title": "...",
  "task_ids": ["task-1", "task-2"],
  "summaries": ["First task summary.", "Second task summary."],
  "total_checks": 8,
  "checks_passed": 8,
  "awaiting_approval": true,
  "all_approved": false,
  "any_rejected": false
}
```

Rules:
- `summaries`: list of non-empty summary strings from validation files (skip empty ones)
- `total_checks`: count of all check keys across all validation files (4 per task normally)
- `checks_passed`: count of checks with `passed: true`
- `awaiting_approval`: true if any task has `gate_tdd_done` stamped in subtasks AND
  its validation exists with `human_approved: false` and `human_rejected` not true
- `all_approved`: true if all tasks have `human_approved: true` in their validation
- `any_rejected`: true if any task has `human_rejected: true` in its validation

### dashboard.html — run-level result hero

Replace the current result hero section with:

**Summary block** (`id="run-summary"`) — shows the joined summaries as plain text paragraphs.
One paragraph per task summary. Large, readable, centred on the deliverable.

**Quality line** — `{checks_passed}/{total_checks} quality checks` as before, but aggregated.

**Run-level buttons** — replace the single `#approve-btn` with:
- `id="run-approve-btn"` — "Approve" (orange pill, same style as current approve-btn)
- `id="run-reject-btn"` — "Reject" (white pill, cyan border)

When **Approve** is clicked:
- POST `/api/approve/{task_id}` for each task_id in the run's `task_ids` sequentially
- Show a loading state while posting
- On all resolved: hide both buttons, show "Approved" badge

When **Reject** is clicked:
- POST `/api/reject/{task_id}` for each task_id sequentially
- On all resolved: hide both buttons, show "Rejected" badge

The deliverable card (`#deliverable-content`, `#deliverable-download`) stays below the
summary — the summary is what you read first, the raw output is available below it.

Poll `/api/run` instead of (or in addition to) `/api/tasks` to populate the result section.
The existing pipeline tracker (`/api/tasks`) stays unchanged.

## Quality criteria

- A non-technical user reading the dashboard can understand what was built without
  opening any file or reading any log
- One click approves or rejects the entire run
- The summary is written in the same voice as the spec — if the spec is in Spanish,
  the summary is in Spanish
- `GET /api/run` returns 200 even when some validation files are missing (partial run)
