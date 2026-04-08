from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SystemMessage
from memory.schema import Task


async def plan(spec: str) -> tuple[list[Task], str]:
    """Ask Claude to break the spec into tasks. Returns tasks and the session_id."""

    structured_output = None
    session_id = None

    async for message in query(
        prompt=f"You are a technical planner. Break this spec into exactly one implementation task:\n\n{spec}",
        options=ClaudeAgentOptions(
            allowed_tools=[],
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id":          {"type": "string"},
                                    "title":       {"type": "string"},
                                    "description": {"type": "string"},
                                },
                                "required": ["id", "title", "description"],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["tasks"],
                    "additionalProperties": False,
                },
            },
        ),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data["session_id"]
            print(f"[planner] session started: {session_id}")
        if isinstance(message, ResultMessage):
            structured_output = message.structured_output

    tasks = [Task(**t) for t in structured_output["tasks"]]
    print(f"[planner] produced {len(tasks)} task(s), session: {session_id}")
    return tasks, session_id
