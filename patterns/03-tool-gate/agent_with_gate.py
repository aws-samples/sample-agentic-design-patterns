def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    gate = ToolGate()   # fresh per conversation

    while True:
        response = client.messages.create(...)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            # Layer 1: Gate
            gate_error = gate.check(block.name)
            if gate_error:
                result = json.dumps({
                    "error": True,
                    "errorCategory": "prerequisite",
                    "isRetryable": False,
                    "message": gate_error,
                })
            else:
                # Layer 2: Override
                hook_result = apply_pre_tool_hook(block.name, block.input)
                if hook_result is not None:
                    result = json.dumps(hook_result)
                else:
                    # Layer 3: Execute
                    result = execute_tool(block.name, block.input)
                    gate.mark_succeeded(block.name, result)

            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": results})
