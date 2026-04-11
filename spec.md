# Harness Dashboard

A local web dashboard that makes the harness JSON human-readable and provides a HITL approval UI.

## Stack

- Language: Python
- Test runner: pytest
- Test command: pytest
- E2E runner: agent-browser
- Dev URL: http://localhost:8000
- Dev command: uvicorn dashboard:app --port 8000
- Framework: FastAPI + vanilla JS (single HTML file, no build step)

## Deliverables

These files must exist when the task is complete, regardless of test coverage:

- `dashboard.py` — FastAPI backend
- `dashboard.html` — single-file frontend, vanilla JS, no build step

`dashboard.html` is not unit-testable but is still required. The TDD skill must
write it during implementation. The validator will check it exists and loads via
agent-browser.

## Features

### Pipeline progress panel

Display `tasks.json` as a visual subtask chain. Each task shows its subtasks in order (planner → context → tdd → validator). Each gate stamp renders as ✅ (true) or ⬜ (false/missing). Updates in real time via SSE as the harness runs.

### Memory cards panel

For each task, render a card showing:
- Context (`memory/{task_id}_context.json`): what, approach, notes
- Decisions (`memory/{task_id}_decisions.json`): list of decisions made
- Validation (`memory/{task_id}_validation.json`): each check with passed/failed status and notes

### Run log timeline

Display `memory/run_log.jsonl` as a chronological event list. Each entry shows: timestamp, tool name, input summary (truncated), response snippet (truncated).

### HITL approval

Validation card shows an **Approve** button when `human_approved: false`. Clicking it sends `POST /approve/{task_id}`, which writes `human_approved: true` to `memory/{task_id}_validation.json` and deletes `memory/waiting_for_human.json` if it exists. Button updates to show approved state without page reload.

### Live updates

- Pipeline progress panel: SSE endpoint (`GET /events`) watches `tasks.json` for changes and streams updates to the client. Client uses `EventSource` to update the panel in real time.
- HITL approval: client polls `GET /tasks/{task_id}/approval` every 3 seconds while `human_approved: false` to detect external approvals (e.g. via CLI).

## API endpoints

- `GET /` — serves `dashboard.html`
- `GET /api/tasks` — returns `tasks.json`
- `GET /api/memory/{task_id}` — returns merged context + decisions + validation for a task
- `GET /api/logs` — returns all entries from `memory/run_log.jsonl` as JSON array
- `GET /api/events` — SSE stream; emits updated `tasks.json` whenever the file changes
- `GET /api/tasks/{task_id}/approval` — returns `{ human_approved: bool }` for the task
- `POST /api/approve/{task_id}` — sets `human_approved: true`, clears sentinel

## Scope

### What gets unit-tested (pytest)
- All API endpoints in `dashboard.py`
- SSE route registration
- HITL approval read/write logic
- Partial memory responses (missing files)

### What is out of scope for unit tests (but still required)
- `dashboard.html` — not unit-testable; written as a static deliverable and
  verified by the agent-browser e2e check
- SSE client-side DOM updates — verified by agent-browser

### Constraints
- No authentication
- No database — all state read from filesystem
- No npm, no build step, no bundler
- Dashboard reads from project root (cwd where uvicorn is started)
