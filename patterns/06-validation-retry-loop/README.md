# Validation-Retry Loop

This pattern is for structured-output pipelines: one model call per document that must produce a schema-conformant JSON object (extracting findings, normalizing tickets, converting free-form input into records). Constrained decoding (`strict: true` / structured-output mode) gets you type-correct, enum-valid, required-fields-present output for free. Leave it on. But the schema can only express *shape*, not *meaning*, and the errors that matter most are usually about meaning. The Validation-Retry Loop validates the decoded output in application code against richer business rules, and on failure feeds the validator's own error message back to the model so it can correct the specific offending field, bounded by a small retry cap.

## The problem

Constrained decoding guarantees the output matches the schema, but cross-field and domain rules live above the schema (e.g. "`source_type_detail` is required when `source_type` is `'other''`"). The model can emit output that passes the decoder yet violates those rules and breaks your system. Retrying with the same prompt reproduces the same failure, and retrying with a vague "try again" just produces a different failure.

## The solution

Validate the model's output in application code against a model richer than the schema can express (in Python, a Pydantic model with `model_validator`). On a validation failure, construct a three-message retry payload (the original user prompt, an assistant turn that echoes the rejected `tool_use` back verbatim, and a user `tool_result` carrying the validator's raw error with `is_error: true`), then call the model again. Bound total attempts with a low cap (two retries past the first attempt is the empirical default).

## Files in this directory

- `finding.py`: the Pydantic `Finding` model, the schema fields plus a `model_validator` enforcing the cross-field business rule (`source_type_detail` required when `source_type == "other"`) that JSON Schema cannot express. Open this first.
- `extract_with_retry.py`: the loop itself. It validates the raw output, and on `ValidationError` rebuilds the three-message retry payload (prompt, echoed prior `tool_use`, error-flagged `tool_result`), re-calls the model, and returns `None` once the cap is exhausted.

## Key points

- **Echo the bad output back to the model.** The assistant turn must contain the exact failed `tool_use` input that was rejected. Without it the model has no referent for the error and guesses at the fix; with it, it diffs the error against its own previous output and corrects the specific field.
- **Mark the tool result `is_error: true`.** That flag is what tells the model the previous turn was wrong and must be redone. The same text as a non-error result leaves it unsure whether it made a mistake at all.
- **Send the validator's raw message.** Pydantic's errors are specific, structured, and actionable. Do not paraphrase, summarize, or wrap them in friendly prose. The specificity is exactly what the model reads to fix the field.
- **Cap the retries and instrument the rate.** Every retry is a full API call (more tokens, more latency on failing cases). Two is a reasonable cap; a rising retry rate signals a shifted source distribution, model regression, or a stale schema description.
- **Some failures are unrecoverable.** If the source document genuinely lacks what the schema asks for, no retry helps. Classify the error (shape violations are usually retry-able; domain mismatches are not) and short-circuit unretry-able cases instead of burning the budget.
- **Document business rules in the schema descriptions.** A rule enforced silently will keep firing until the model has a reason to know it exists; describe it where the model can see it.

## Related patterns

- **Structured Error Classification (Ch. 7)**: supplies the `isRetryable` vocabulary to distinguish retry-able shape errors from unretry-able domain mismatches, shared with tool-error handling.
- **Confidence-Based Routing (Ch. 8)**: routes low-confidence-but-well-formed output to a reviewer; catches the well-formed-but-wrong cases this loop cannot.
- **Review Pass (Ch. 9)**: addresses the semantic errors (a claim that satisfies every rule but is subtly wrong) that validation alone does not catch.
