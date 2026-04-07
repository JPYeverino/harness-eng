import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher, ResultMessage


# STEP 3: Write your hook here
# A hook is just an async function. It receives input_data about the tool call.
# Return {} when done (or a dict with optional "decision": "block" to cancel it).
async def log_tool_use(input_data, tool_use_id, context):
    print(input_data)
    tool_name = input_data.get("tool_name", "unknown")
    # TODO: print something useful from input_data so you can see what's happening
    return {}


async def main():
    async for message in query(
        # STEP 4: Change this prompt to something that will trigger a tool use
        # Try: "What files are in the current directory?"
        prompt="Check online what day is today",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Bash"],
            # STEP 5: Wire up the hook — uncomment this block:
            hooks={
                "PreToolUse": [HookMatcher(matcher=".*", hooks=[log_tool_use])]
            }
        ),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)


anyio.run(main)
