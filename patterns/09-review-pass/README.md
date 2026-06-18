# Review Pass

A primary agent pass usually produces fine output, but occasionally it is incomplete or misleading in ways no schema or confidence score can catch: a reply that addresses two of three customer concerns, a refund confirmation missing the reference number, a vague explanation where specifics were needed. The information was in the tool results; it just did not make it into the draft. Review Pass adds a second pass that judges the draft against an explicit, binary rubric before it ships, catching the rendering failures that more primary-prompt instructions cannot reliably engineer away.

## The problem

There is a class of errors that a valid schema, a high confidence score, and a confident model all fail to surface. The output is structurally valid and the underlying reasoning is sound. The failure is in the final rendering, where the draft is incomplete or overstated. Piling more instructions onto the primary prompt yields diminishing returns and then fragile prompts, so the gap has to be closed somewhere other than the primary pass.

## The solution

After the primary pass produces a draft, run a second pass that reviews that draft against an explicit rubric, then choose the variant by the kind of error you need to catch. The **Self-Evaluation** variant asks the same model instance to check its own draft against a binary checklist and revise if any item fails. It is cheap (one extra call, same context) and effective at completeness and formatting misses. The **Critic-Agent** variant hands the draft to a separate agent with a fresh context, a different system prompt, and no tools, so it judges only what is on the page. It is more expensive, but it catches the overreach a model is poorly placed to spot in its own committed narrative. Default to Self-Evaluation; escalate to Critic-Agent when output ships without human review, the primary model has a stake in the conclusion, or downstream errors are expensive to detect. Apply review selectively (e.g. a cheap heuristic routing only complex inputs to review) to avoid doubling cost and latency on every turn.

## Files in this directory

- `self_eval.py`: Self-Evaluation variant. A binary, task-specific checklist plus a wrapper that runs the primary pass, then re-invokes the same model to review (and possibly revise) the draft against the rubric.
- `critic_agent.py`: Critic-Agent variant. An agent definition framed as an external reviewer that returns a structured JSON list of issues, with an intentionally empty `tools` list.

## Key points

- Rubric design decides whether the pattern works: items must be **binary** (yes/no), **specific to the task** ("are all refund reference numbers present", not "is the response helpful"), and **assessable from the output alone** (not "did we call the right tools"; the reviewer cannot see that). Five items is plenty; fifty items is a review pass that itself needs review.
- The critic's `tools` list is **empty on purpose**. A critic that can re-run searches becomes a second primary pass, not an independent reviewer. The point is to judge what is already on the page.
- Apply the review **selectively**. A lightweight heuristic on the input routes simple requests straight through and reserves the extra call for complex ones, since one review call per turn doubles cost and adds latency.
- Constrain revision: a pass told to "revise if deficient" tends to over-correct, so instruct it to "make the minimum change required; preserve wording that is already correct."
- Both variants have **shared blind spots**. Self-Evaluation agrees with the primary model's own factual beliefs; Critic-Agent agrees with facts both instances share. For high-stakes factual claims, pair the review with retrieval-backed verification. A second parametric model is not a substitute.
- Treat the rubric as a first-class, versioned artifact tied to your eval harness. A rubric that drifts from the real quality bar is worse than none because it produces confident false negatives, and the same rubric applied across a test set is exactly an LLM-as-judge evaluation.

## Related patterns

- **Agentic Loop**: the primary pass that produces the draft the review pass evaluates.
- **Coordinator-Subagent Hierarchy (Ch. 10)**: the Critic-Agent is a preview of this, a subagent with empty tools invoked as a review step.
- **LLM-as-judge evaluation**: the aggregate form of Self-Evaluation (the same rubric across a test set rather than a single output).
- **LLM-as-a-jury**: the next step along the reviewer-independence axis (heterogeneous models voting), where Review Pass ends and the jury literature begins.
