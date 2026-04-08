from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage, AssistantMessage, TextBlock
from memory.schema import ContextDoc, TDDResult


async def run_tdd(ctx: ContextDoc, cwd: str, resume: str) -> TDDResult:
    """Runs the TDD cycle. Resumes from context session so prior plan is in memory."""

    structured_output = None

    print(f"[tdd] resuming session: {resume}")
    async for message in query(
        prompt="""
You are a TDD engineer. Follow these steps strictly in order:

1. Write failing tests. Run pytest. Confirm it fails.
2. Write a brute force implementation. Run pytest. Confirm it passes.
3. If tests already exist and pass, evaluate whether the current implementation can be improved. If yes, refactor to the optimal solution. Run pytest. Confirm it still passes.
4. Report each key decision made — why brute force first. 
""",
        options=ClaudeAgentOptions(
            cwd=cwd,
            resume=resume,
            allowed_tools=["Read", "Write", "Bash"],
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "success":   {"type": "boolean"},
                        "test_file": {"type": "string"},
                        "impl_file": {"type": "string"},
                        "decisions": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["success", "test_file", "impl_file", "decisions"],
                    "additionalProperties": False,
                },
            },
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print(f"[tdd] session: {message.data['session_id']}")
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[tdd] {block.text}")
        if isinstance(message, ResultMessage):
            structured_output = message.structured_output

    print(f"[tdd] done — success: {structured_output['success']}")
    return TDDResult(task_id=ctx.task_id, **structured_output)
