import json
from anthropic import AnthropicBedrock

client = AnthropicBedrock()

def run_agent(user_message: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="global.anthropic.claude-opus-4-8",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": execute_tool(block.name, block.input),
                })
            messages.append({"role": "user", "content": results})
            continue

        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

    raise RuntimeError(f"Exceeded max_turns ({max_turns})")
