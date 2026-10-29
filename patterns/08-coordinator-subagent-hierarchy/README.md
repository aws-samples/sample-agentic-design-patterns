# Coordinator-Subagent Hierarchy

When a task is too large for one agent to handle coherently, this pattern decomposes it into a star topology: a coordinator agent splits the work into non-overlapping sub-tasks, dispatches narrow subagents in parallel, then merges their structured results into a single synthesized answer. It solves the three ways a single large agent degrades (context bloat, importance-blind processing of tool results, and partial failures cascading into total failures) by giving each subagent a small, high-relevance context and letting the coordinator see structure rather than detail.

## The problem

A single agent running a large task loses coherence: its context accumulates past the point where attention stays reliable, its output correlates with the arrival order of tool results rather than their importance, and one failed step fails the whole run. Each issue is fixable alone, but together they signal that the task wants to be decomposed. The catch is that decomposition shifts complexity into a new coordination problem rather than eliminating it.

## The solution

Structure the system as a coordinator agent that decomposes the task into sub-tasks with mutually exclusive domains, dispatches subagents concurrently, merges their structured results, *preserves* rather than reconciles conflicts, and synthesizes the final answer. Each subagent is a narrow agent with its own tools, its own output format, and hard limits on tool calls; a cheaper model is usually fine at this layer because the coordinator does the hard reasoning. Reach for a framework (here, the Claude Agent SDK) for concurrent dispatch and message plumbing rather than hand-writing nested loops. Conflict detection and importance-based reordering run in the coordinator's own code, before synthesis, not in the prompt.

## Files in this directory

- `web_search_agent.py`: a subagent definition, a narrow, cheap-model agent with explicit hard limits on tool calls and a strict structured-JSON output schema.
- `coordinator_prompt.py`: the coordinator's system prompt, with the three load-bearing clauses (parallel emission, domain partitioning, conflict preservation) made explicit.
- `run_pipeline.py`: the single framework call that wires the coordinator to its subagents and runs the research pipeline.
- `post_process.py`: coordinator-side code for conflict detection and importance reordering, the two responsibilities done in code rather than in prompt.

## Key points

- **Emit all subagent (`Task`) calls in a single response.** Parallelism comes from one response containing all dispatches; without the explicit instruction the coordinator defaults to slow sequential dispatch.
- **Partition domains at dispatch time, not at synthesis.** Duplicate findings are the clearest sign of a coordinator bug. The fix is non-overlapping domain boundaries stated in each subagent's prompt (including what it should *not* cover), never deduplication after the fact.
- **Preserve conflicts; never average or discard.** When credible sources disagree, the coordinator keeps both with full attribution. `detect_conflicts` only flags a real conflict when claims come from *different* source URLs and all have confidence above 0.5; same-source overlap is not a conflict.
- **Design for partial results from the start.** A subagent failure is one coverage gap, not a run failure; record gaps as first-class output and proceed with the rest.
- **Reorder for synthesis to beat lost-in-the-middle.** `reorder_for_synthesis` ranks findings by confidence and places the highest-importance ones at the front and back of the input, mitigating the documented quality drop when key findings land in the middle.
- **Cost scales with subagent count, latency does not.** Four concurrent subagents are four API calls: you pay for latency reduction, not total compute. Instrument tail latency, since one slow subagent silently eats the parallel gains.

## Related patterns

This pattern composes several smaller techniques: domain partitioning, parallel execution, error propagation with partial results, conflict detection, and lost-in-the-middle mitigation. It builds on the [Agentic Loop](../01-agentic-loop/) as the mental model of what the framework runs, and the [Review Pass](../07-review-pass/) Critic-Agent variant slots in naturally as an extra reviewing subagent before delivery.
