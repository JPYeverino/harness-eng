import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock
from spec import SPEC


async def main():
    print("=== Harness ===")
    async for message in query(
        prompt=f"The spec is:\n\n{SPEC}",
        options=ClaudeAgentOptions(
            allowed_tools=["Skill", "Read", "Write", "Bash", "Glob"],
            setting_sources=["user", "project"],
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        if isinstance(message, ResultMessage):
            print(f"\ndone — cost: ${message.total_cost_usd:.4f}")


anyio.run(main)
