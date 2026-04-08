from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage
from memory.schema import Task, ContextDoc


async def create_context(task: Task, resume: str) -> tuple[ContextDoc, str]:
    """Given a task, produce a ContextDoc. Resumes from planner session."""

    structured_output = None
    session_id = None

    print(f"[context] resuming session: {resume}")
    async for message in query(
        prompt=f"""
You are a senior engineer planning an implementation.

Task: {task.title}
Description: {task.description}

Produce a context document covering:
- what: what needs to be built
- approach: start with brute force, then describe the optimal solution and why it's better
- notes: anything the implementing agent should know
""",
        options=ClaudeAgentOptions(
            allowed_tools=[],
            resume=resume,
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "what":     {"type": "string"},
                        "approach": {"type": "string"},
                        "notes":    {"type": "string"},
                    },
                    "required": ["what", "approach", "notes"],
                    "additionalProperties": False,
                },
            },
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data["session_id"]
            print(f"[context] session: {session_id}")
        if isinstance(message, ResultMessage):
            structured_output = message.structured_output

    print(f"[context] done, session: {session_id}")
    return ContextDoc(task_id=task.id, **structured_output), session_id
