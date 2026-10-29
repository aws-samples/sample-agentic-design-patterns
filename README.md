# Agentic Design Patterns

This repository collects eight design patterns for building reliable LLM agents, each
with a short write-up and Python code using the Anthropic SDK on Amazon Bedrock. Every
pattern lives in its own directory with a `README.md` that covers the problem it solves,
the solution, the files to read (and in what order), and how it relates to the other
patterns.

These are **illustrative fragments**, not a turn-key application. Several snippets
call helpers that are left for you to implement, for example `SYSTEM_PROMPT`, `TOOLS`,
`execute_tool(...)`, `lookup_transaction_amount(...)`, and the per-pattern tool
implementations. The code shows each pattern's mechanics so you can port the shape
into your own agent.

Because the security-critical logic lives in those undefined helpers (what
`execute_tool` permits, how tool inputs are checked), the snippets show the
*pattern*, not a complete security boundary. When you port any of this into a real
agent, your own implementation must validate every tool's inputs and enforce
authorization; the patterns here assume you have done so.

## Repository layout

```
sample-agentic-design-patterns/
├── README.md
├── requirements.txt
├── LICENSE
└── patterns/
    ├── 01-agentic-loop/
    ├── 02-deterministic-override/
    ├── 03-tool-gate/
    ├── 04-validation-retry-loop/
    ├── 05-structured-error-classification/
    ├── 06-confidence-based-routing/
    ├── 07-review-pass/
    └── 08-coordinator-subagent-hierarchy/
```

The numbering is a suggested reading order: the Agentic Loop comes first because the
other patterns build on it.

## Patterns

| # | Pattern | What it does |
|---|---------|--------------|
| 01 | [Agentic Loop](patterns/01-agentic-loop/) | The control loop that turns a single model call into a multi-turn, tool-using agent. |
| 02 | [Deterministic Override](patterns/02-deterministic-override/) | Move a must-always-hold rule out of the prompt and into a code hook that intercepts a tool call before it executes. |
| 03 | [Tool Gate](patterns/03-tool-gate/) | Enforce required ordering between tool calls by tracking, in code, which prerequisites have already succeeded. |
| 04 | [Validation-Retry Loop](patterns/04-validation-retry-loop/) | Validate structured output against richer business rules than a schema can express, and feed the error back for a bounded retry. |
| 05 | [Structured Error Classification](patterns/05-structured-error-classification/) | Replace error strings with a structured error object (`errorCategory`, `isRetryable`, `message`) so recovery behavior is deterministic. |
| 06 | [Confidence-Based Routing](patterns/06-confidence-based-routing/) | Attach a coarse, named confidence category to each output and route low-confidence results to review. |
| 07 | [Review Pass](patterns/07-review-pass/) | Add a second pass that judges a draft against an explicit binary rubric before it ships. |
| 08 | [Coordinator-Subagent Hierarchy](patterns/08-coordinator-subagent-hierarchy/) | Decompose a large task into a coordinator that dispatches narrow subagents in parallel and merges their structured results. |

## Getting started

The code uses the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
against **Amazon Bedrock** (`from anthropic import AnthropicBedrock`) and
[Pydantic](https://docs.pydantic.dev/) (in the Validation-Retry Loop).

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

To actually invoke a model you need **Amazon Bedrock access** and AWS credentials in
your environment (the `AnthropicBedrock()` client picks them up from the standard AWS
credential chain: `AWS_PROFILE`, `AWS_REGION`, environment variables, or an instance
role). You also need model access enabled for the Claude model the snippets reference
(`global.anthropic.claude-opus-4-8`). Swap in whichever Claude model id you have
access to.

## License

Sample/illustrative code, provided **as-is** under the [MIT License](LICENSE).

This is sample code, for non-production usage. You should work with your security and
legal teams to meet your organizational security, regulatory, and compliance
requirements before deployment.
