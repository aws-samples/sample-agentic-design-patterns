# Deterministic Override

When an agent can take actions with real consequences, some rules must hold *every* time, not most of the time: "refunds above $500 require human review," "never email a suppressed address," "block all tool calls during maintenance." A system prompt can push the model to ~99% compliance but never reaches 100%, and for a rule that must always hold, a 1% failure rate is simply broken. Deterministic Override moves that one rule out of the probabilistic layer (the prompt) and into deterministic code: a hook intercepts the specific tool call before it executes and, when a precisely-stated condition fires, returns a canned result that never reaches the real tool.

## The problem

The system prompt and tool descriptions both state the rule, yet under unusual inputs, a weaker model, or a long conversation that pushed the rule out of context, the model still crosses the line, rarely, but repeatedly, and each crossing is expensive. You cannot prompt-engineer your way to a guarantee. The rule is probabilistic when you state it to the model, but your system needs it to be deterministic to be safe.

## The solution

Intercept the tool call at the one seam in the agentic loop: between the model's `tool_use` block and the call to the tool's implementation. A hook function receives the tool name and input and returns `None` to let the call proceed, or a result dict to short-circuit it. When the dict is returned, the loop serializes it as the tool result and the model continues as if the tool had run, typically narrating a structured flag (e.g. `"escalated": true`) to the user per instructions in the system prompt. The prompt still shapes the *response* to the override; it no longer *enforces* the rule. The hook does that.

Use this only for rules that genuinely require 100% enforcement. If you can name the firing condition precisely in code and it must always hold, it belongs in the hook; if the rule involves judgment, tone, or intent, it belongs in the prompt.

## Files in this directory

Read in this order:

- `pre_tool_hook.py`: the deterministic hook. It matches `process_refund`, looks up the true refund amount from a source of truth, and returns an escalation result dict when it exceeds the threshold (otherwise `None`).
- `dispatch.py`: the one-point change to the agentic loop. Call the hook, take the override path (serialize its dict) when it returns a result, otherwise fall through to normal tool execution.

## Key points

- **Don't trust the model's parameters in the condition check.** A schema may mark `amount` as optional and the model may send `None`; a naive `tool_input.get("amount", 0) > THRESHOLD` evaluates `None > 500` as `False` and lets the call through. Derive the condition from deterministic data: the hook looks the amount up via `transaction_id` from its own ledger.
- **The hook returns `None` to allow, a dict to override.** That single contract is what lets the loop short-circuit cleanly at one seam.
- **The rule lives in two places and they can drift.** The hook is canonical; the system prompt is a shadow that must be maintained in lockstep so the model narrates the override instead of fighting it. Keep them in the same file if you can.
- **The model will still try.** The hook stops the tool from running, not the model from requesting it. Overridden calls show up in logs: useful signal for tracking prompt quality, but it surprises people who expect enforcement to also suppress the attempt.
- **Overuse is the real failure mode.** Encoding every preference as an override turns the agent into a decision tree with a language model stapled to the front. Relocating twenty rules into code relocates complexity rather than eliminating it.
- **Shape the override result like a structured error.** It carries a known flag, a message, and a category; adopting a single convention early keeps intercept results and tool errors composable.

## Related patterns

- **Tool Gate (Ch. 5)**: enforces *ordinal* rules ("tool A cannot run before tool B succeeds") that need state across calls. It sits at the same seam and composes: Gate checks first, Override checks second, execution runs third.
- **Structured Error Classification (Ch. 7)**: the convention for the structured shape (flag, message, category) the override returns; adopt it before you have more than one kind of intercept result.
