# Structured Error Classification

Tools fail in fundamentally different ways (a mistyped account number, a timed-out payment processor, a frozen account, a skipped prerequisite), but when a tool returns its failure as a bare string, the model has no reliable way to tell those situations apart and routinely picks the wrong recovery behaviour. This pattern replaces error strings with structured error objects that carry an explicit `errorCategory`, an `isRetryable` hint, and a human-readable `message`, and teaches the system prompt how to respond to each category. The result is a shared error vocabulary that makes agent recovery behaviour deterministic instead of contingent on the model reading the "mood" of a sentence.

## The problem

When a tool returns an error as a string, the model guesses the kind of failure from the phrasing, and those guesses are wrong often enough to matter. "Account not found" and "service temporarily unavailable" can both produce "sorry, please try again later," correct for the transient case, but for the validation case it just invites another wrong account number. A single error string collapses meaningfully different situations into one surface, and the right response (retry, ask the user, explain a constraint, run a missing step) depends on which situation it actually is.

## The solution

Return errors as structured objects carrying a `category`, a `retry` hint, and a human-readable `message`, produced by one shared helper that every tool calls. Four categories cover most production agents:

- `transient`: infrastructure failure (timeout, service unavailable, rate limit) where the tool's own retries are exhausted.
- `validation`: input is malformed or does not exist (mistyped account, missing field, unparseable date).
- `permission`: the operation is not allowed (frozen account, insufficient privilege, compliance block).
- `prerequisite`: a required prior step has not completed (produced by Tool Gate).

The system prompt maps each category to a behaviour: explain-and-ask for `validation`, explain-and-suggest-alternative for `permission`, retry-once for `transient` when `isRetryable: true`, and call-the-missing-tool-then-retry for `prerequisite`. The prompt also instructs the model never to expose raw error JSON and to translate errors into clear, empathetic language.

## Files in this directory

Read in this order:

- `error_payload.json`: the error object shape, with `error`, `errorCategory`, `isRetryable`, and `message` fields, shown for a `validation` failure.
- `tool_error.py`: the shared helper every tool calls; serialises a category, retry hint, and message into the standard JSON error shape.
- `get_account_info.py`: an example tool that uses the helper, returning a `validation` error for an unknown account and a `permission` error for a frozen one, and plain success JSON otherwise.

## Key points

- Default `isRetryable` to `false`. Set it `true` only when the tool is genuinely idempotent and the failure leaves the system in a pre-call state. A non-idempotent tool that returns `isRetryable: true` causes duplicate side effects on retry.
- Prefer retrying transient failures *inside* the tool with exponential backoff. By the time a transient error reaches the agent, the tool's retry budget should be exhausted, so the agent's job is to inform the user, not retry further, which is why `isRetryable: false` is usual at the agent layer.
- The taxonomy is a convention you impose on your own layer, not a global standard. Keep one shared taxonomy across your tools; wrap third-party tools at the boundary to adapt their strings, exceptions, or HTTP codes into it rather than teaching the agent two conventions.
- A taxonomy is an API: once a category is in production, renaming or removing it is a breaking change. Start small, four categories, and add a fifth (`rate_limited`, `escalated`) only deliberately. Six is a warning sign; a seventh means something else is trying to be expressed.
- Not every non-happy outcome is an error. A search that returns multiple matches has *succeeded* but is ambiguous. Use a separate flag (e.g. `ambiguous: true` with a `matches` list), and reserve `error: true` for genuine failures to keep the taxonomy clean.
- Categorisation is a judgment call (is an expired token `permission` or `transient`?). Document those decisions outside the tools themselves or they will drift.

## Related patterns

The same result shape is reused across the language: [Deterministic Override](../02-deterministic-override/) emits `escalated: true` using these conventions, [Tool Gate](../03-tool-gate/) returns `errorCategory: "prerequisite"`, [Validation-Retry Loop](../04-validation-retry-loop/) uses the `isRetryable` concept, [Coordinator-Subagent Hierarchy](../08-coordinator-subagent-hierarchy/) propagates subagent failures in this shape, and [Confidence-Based Routing](../06-confidence-based-routing/) applies the same shape to success metadata like `confidence` and `requires_review`.
