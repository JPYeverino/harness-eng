# Project

Skills are in `.claude/skills/`. To run the full harness, invoke the `orchestrator` skill.

## Known context

- `phases/` exists alongside the skills-based harness. It is the earlier multi-session implementation (one `query()` call per phase via the Agent SDK). It is kept intentionally as a learning reference — do not wire it into `main.py` or treat it as the active harness.
