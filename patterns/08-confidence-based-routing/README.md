# Confidence-Based Routing

In a high-volume structured-output pipeline, most extractions are straightforward and ship fine, but a non-trivial fraction (hedged claims, contested findings, ambiguous sources) needs a second look. Reviewing everything kills the cost benefit of automation; reviewing nothing ships uneven quality into the downstream product. Confidence-Based Routing has the model attach a coarse, named confidence category to each output, then branches on that category: high-confidence outputs auto-accept, everything else goes to a review path. It decouples cost from quality so straightforward inputs stay automated and ambiguous ones get the attention they need.

## The problem

Structural validation tells you an output is schema- and rule-conformant, but it cannot tell you which outputs the model was unsure about, and those uncertain outputs are precisely the ones that most need review. Without a signal to separate the routine ~90% from the questionable ~10%, you are forced to either review everything (no automation savings) or review nothing (uneven quality shipping into research synthesis, medical, or legal contexts where that is catastrophic).

## The solution

Add a confidence field to the output schema as a small set of named categories (`high`, `medium`, `low`, `uncertain`) rather than a 0.0–1.0 float. Teach the model what each category means in the system prompt by tying it to observable linguistic markers in the source (specific statistics and named sources for `high`, hedging language for `low`, speculative or contradicted claims for `uncertain`). A small routing function then branches by category: `high` auto-accepts, everything else routes to review. Which categories count as auto-accept is a tunable policy decision that can differ per domain. Aggregating the category counts over time turns confidence into a free operational metric for spotting where the extraction prompt is weak.

## Files in this directory

- `route.py`: the routing layer. It classifies each finding's confidence category against an `AUTO_ACCEPT` set and splits a result's findings into auto-accept and review lists.
- `analyse.py`: the aggregation/observability layer. It tallies confidence categories by source type and computes a per-source review rate.

## Key points

- **Use named categories, not a float.** Verbalised continuous confidence is badly calibrated at sub-tenth precision (0.85 vs 0.87 is noise); coarse categorical bins are stable, explainable, and the reason the pattern works.
- **You must define what each category means.** Asked for confidence with no guidance, the model returns 0.95 for everything because it reads "confidence" as extraction fidelity, not evidence strength. Explicit, marker-based scoring guidelines in the system prompt are what turn the field into a signal.
- **The auto-accept set is a policy decision, not a constant.** `{"high"}` is the safe default; `{"high", "medium"}` ships more when review capacity is the bottleneck. Different domains in the same pipeline can warrant different policies. Measure downstream quality at each setting.
- **This does not catch confident hallucinations.** A false claim labelled `high` routes straight to auto-accept and looks identical to a true one. This is triage over self-reported uncertainty, not a correctness guarantee. Layer a Review Pass on top where high-confidence-wrong is expensive.
- **Calibration drifts.** A model upgrade, prompt change, or input-distribution shift moves the category distribution without moving your policy. Re-measure after any material change; do not set-and-forget.
- **Confidence is not a probability.** The label is the model's self-report against the rubric, not a calibrated frequentist claim. Do not expose it to external consumers as if it were.

## Related patterns

- **Validation-Retry Loop**: the upstream pattern that guarantees outputs are schema- and rule-conformant before they reach this routing layer.
- **Review Pass (Ch. 9)**: the natural follow-on. Its critic-agent variant handles the low-confidence review path, and either variant guards the high-confidence-but-wrong outputs this layer cannot catch.
- **Coordinator-Subagent Hierarchy (Ch. 10)**: composes forward; a coordinator synthesising findings should respect confidence, annotating low-confidence findings as contested rather than presenting them as well-supported.
