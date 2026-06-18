# Agentic Loop

The Agentic Loop is the control flow that turns a single model call into a multi-turn agent. A single request-response works for questions, but a real task ("refund the AnyCompany Streaming charge on account ACC-001") is a chain of dependent tool calls (look up the account, find the transaction, check eligibility, process the refund) where each step is conditioned on the previous result. The provider API returns one response per call and never loops on your behalf, so you write the loop: call the model, run any tools it asks for, feed the results back, and repeat until the model says it is done.

## The problem

The model produces intent; your code must produce continuation. When the model's response says "call this tool," the next API call must include that tool's result or the model cannot reason about what to do next; when it says "I'm done," the loop must stop. Nothing in the API enforces either behavior. Everything between those two signals is yours to get right. Hand-written loops break in subtle ways because the response is a list of content blocks (not just text), tool results must be paired to their calls by id, and the loop has no natural termination.

## The solution

Drive a bounded loop over the message history. Call the model with the full history. If `stop_reason` is `end_turn`, extract the text and return. If `stop_reason` is `tool_use`, execute each requested tool, then append two things: the model's entire response content as the assistant turn, and a single user message containing every tool result. Call again. Cap the iteration count and raise a clear error when the cap is hit, so a model that keeps finding new work cannot run forever.

## Files in this directory

- `run_agent.py`: the complete loop in about thirty lines. It calls `AnthropicBedrock`, appends `response.content` verbatim, dispatches tools via an `execute_tool` seam, batches `tool_result` blocks into one user message, branches on `stop_reason`, and enforces a `max_turns` cap.

## Key points

- **Append the entire response content, not just the text.** The model reads back its own previous turn on every iteration; if its `tool_use` blocks are stripped out, it goes amnesic and behaves erratically.
- **Match `tool_use_id` to the originating block's `id` verbatim.** Copy it straight from the `tool_use` block; do not regenerate, reuse, or shorten it. The pairing is what tells the model which call a result answers; the API rejects a missing/mismatched id and silently misleads the model on a structurally-valid-but-wrong one.
- **Batch tool results in one user message.** If the model emitted three `tool_use` blocks (it expects them to run in parallel), return one user message with three `tool_result` blocks, not three messages with one each.
- **The turn cap is not optional.** `end_turn` is the only termination signal; an unbounded loop will eventually find a task that loops forever, and the bill arrives before the alert does. Ten is a reasonable default.
- **Token cost grows faster than loop depth suggests.** Every iteration resends the full history, so a ten-turn task sends the first turn ten times. Prompt caching softens this; without it, long loops amortise poorly.
- **Leave a seam at tool dispatch.** Later patterns each modify exactly one point: between the model's tool call and the tool's execution. Writing the loop as a tight function with no seam there forces a rewrite for every later pattern.
- **The bare loop has no tool authorization.** `execute_tool` runs whatever the model selects, with no ordering, permission, or input checks. That is by design, the loop is the foundation the other patterns build on, but the loop alone is unsafe for sensitive tools (refunds, writes, anything with side effects). Pair it with the Tool Gate (05) for ordering and the Deterministic Override (04) for must-hold rules, and validate every tool's inputs before acting on them, before exposing it to anything consequential.

## Related patterns

- **Deterministic Override**: intercepts specific tool calls before they execute (e.g. a dollar threshold or compliance rule).
- **Tool Gate**: blocks calls whose prerequisites are unsatisfied (e.g. a refund before an eligibility check). With Override, dispatch becomes gate → override → execute.
- **Structured Error Classification**: the failure vocabulary those dispatch-step patterns return so the model can reason about what went wrong.
- **Validation-Retry Loop**: shares this shape but operates on producing/validating structured output rather than dispatching tools.
- **Coordinator-Subagent Hierarchy**: nests this loop inside another, a coordinator loop dispatching subagents whose loops run in parallel.
