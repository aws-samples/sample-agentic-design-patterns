# Inside the loop, in the tool_use branch:
hook_result = apply_pre_tool_hook(block.name, block.input)
if hook_result is not None:
    result = json.dumps(hook_result)          # override path
else:
    result = execute_tool(block.name, block.input)  # normal path
