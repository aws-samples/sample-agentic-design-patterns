# Tool Gate

When tools must run in a specific order (look up the account, then fetch transactions, then check eligibility, then process the refund), tool descriptions that cross-reference each other ("only call `process_refund` after `check_refund_eligibility`") raise compliance but never guarantee it. A less capable model, an adversarial message, or a model upgrade can occasionally produce an out-of-order call that executes nonsense or fails confusingly. Tool Gate makes the remaining ordering violations impossible by tracking, in code, which tools have already succeeded in the current conversation and refusing to run a tool until its prerequisites are satisfied.

## The problem

Ordering between tool calls is semantically required, but probabilistic guidance in tool descriptions does not guarantee it. Most of the time the model orders calls correctly; occasionally it does not, and the downstream tool runs against missing or incorrect state. Ordering is a property *across* calls ("has the prerequisite already succeeded in this conversation?"), which a per-call check cannot answer because it lacks the conversational state.

## The solution

Track which tools have succeeded so far in the conversation. Before any tool runs, check its prerequisites against that state; if any are unsatisfied, return a structured error naming the missing tools and refuse to execute. The gate sits in front of the override hook in the dispatch seam, so a tool call now passes through three layers (gate check, override hook, execution), any of which can short-circuit. The structured error uses a `prerequisite` category that the system prompt teaches the model to recognize, so the model calls the missing tool and retries on its own. Crucially, a tool only counts as satisfied when it actually *succeeds*: a return that carries a structured error does not mark the prerequisite as met.

## Files in this directory

- `tool_gate.py`: the `ToolGate` class, a per-tool prerequisite graph, a check that returns a human-readable error naming the missing prerequisites, and `mark_succeeded`, which records a tool as satisfied only when its result is not a structured error.
- `agent_with_gate.py`: the three-layer dispatch inside `run_agent`. Gate check, then override hook, then execution, with the gate instantiated fresh per conversation.

## Key points

- **Occurrence, not content.** The gate enforces that a prerequisite tool *ran and succeeded*, not what it returned. Content-sensitive rules ("only refund if eligibility returned `eligible: true`") belong to the Deterministic Override; the two compose.
- **Success is not the same as completion.** `mark_succeeded` parses the result and only records the tool as satisfied when `error` is falsy: a failed account lookup must not satisfy a downstream prerequisite. (Non-JSON or unparseable results fail closed: they are treated as failure and do not satisfy the prerequisite, so an ambiguous result never unlocks a downstream gated tool.)
- **Fresh gate per conversation.** The gate is instantiated inside `run_agent`, never as a module-level singleton, so parallel users never share gate state.
- **Layer order matters.** Gate check runs before the override hook, which runs before execution; only successful execution feeds back into `mark_succeeded`. A gate rejection skips both the hook and the tool.
- **Structured, retryable-aware error shape.** Rejections return `{ error: true, errorCategory: "prerequisite", isRetryable: false, message }`; the message names each missing prerequisite by name so the model's recovery is obvious and reliable.
- **Gate only the load-bearing tools.** Keep tool descriptions, since they keep the rejection rate (and round-trips) low. Reserve gates for the small set of orderings that genuinely matter; if every tool gates every other tool, you have built a state machine and should consider a scripted pipeline instead.

## Related patterns

- **[Deterministic Override](../02-deterministic-override/)**: enforces conditional rules on a single call's content; the gate enforces ordinal rules across calls. They compose (eligibility *ran* is a gate concern; eligibility *result* is an override concern).
- **[Structured Error Classification](../05-structured-error-classification/)**: formalizes the structured error shape (`errorCategory`, `isRetryable`) that the gate borrows; the gate's error taxonomy should match your tools'.
