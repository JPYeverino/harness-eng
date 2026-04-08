import anyio
import json
from pathlib import Path
from spec import SPEC
from phases.planner import plan
from phases.context import create_context
from phases.tdd import run_tdd

async def main():
    # Phase 1: plan
    print("=== Planning ===")
    tasks, planner_session = await plan(SPEC)

    # Phase 2: context for each task — resumes from planner session
    print("\n=== Context Creation ===")
    contexts: dict[str, object] = {}
    context_sessions: dict[str, str] = {}
    for task in tasks:
        ctx, ctx_session = await create_context(task, resume=planner_session)
        contexts[task.id] = ctx
        context_sessions[task.id] = ctx_session
        print(f"  WHAT:     {ctx.what[:80]}...")
        print(f"  APPROACH: {ctx.approach[:80]}...")

    # Phase 3: TDD — resumes from context session so agent already knows the plan
    print("\n=== TDD ===")
    for task in tasks:
        result = await run_tdd(contexts[task.id], cwd=".", resume=context_sessions[task.id])
        print(f"  success:   {result.success}")
        print(f"  test_file: {result.test_file}")
        print(f"  impl_file: {result.impl_file}")
        print(f"  decisions:")
        for d in result.decisions:
            print(f"    - {d}")

        memory_file = Path("memory") / f"{task.id}_decisions.json"
        memory_file.write_text(json.dumps({
            "task_id":   result.task_id,
            "test_file": result.test_file,
            "impl_file": result.impl_file,
            "decisions": result.decisions,
        }, indent=2))
        print(f"  saved → {memory_file}")

    # TODO: Phase 4 — git.py  (commit, push, PR)


anyio.run(main)
