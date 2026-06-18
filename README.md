# Agentic Design Patterns: Companion Code

This repository is the companion code for the AWS Prescriptive Guidance whitepaper
**_Agentic Design Patterns_** ([PDF](agentic-design-patterns-prescriptive-guidance.pdf)).
Every snippet here is extracted **verbatim** from the paper. It is the same code that
appears inline in each chapter, lifted into runnable files and organized one directory
per pattern.

These are **illustrative fragments**, not a turn-key application. Several snippets
reference helpers that the paper defines in the surrounding narrative or in the source
workshop, for example `SYSTEM_PROMPT`, `TOOLS`, `execute_tool(...)`,
`lookup_transaction_amount(...)`, and the per-pattern tool implementations. They are
shown the way they appear in the paper so you can read each pattern's mechanics
directly against the prose, then port the shape into your own agent. Read each
pattern's `README.md` for the context, the problem it solves, and which file to open
first.

Because the security-critical logic lives in those undefined helpers (what
`execute_tool` permits, how tool inputs are checked), the snippets show the
*pattern*, not a complete security boundary. When you port any of this into a real
agent, your own implementation must validate every tool's inputs and enforce
authorization, the patterns here assume you have done so.

## Repository layout

```
agentic-design-patterns-code/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
└── patterns/
    ├── 03-agentic-loop/
    ├── 04-deterministic-override/
    ├── 05-tool-gate/
    ├── 06-validation-retry-loop/
    ├── 07-structured-error-classification/
    ├── 08-confidence-based-routing/
    ├── 09-review-pass/
    └── 10-coordinator-subagent-hierarchy/
```

Each pattern directory contains the extracted code files plus a `README.md` that
distills the corresponding whitepaper chapter.

## Patterns

| # | Pattern | What it does |
|---|---------|--------------|
| 03 | [Agentic Loop](patterns/03-agentic-loop/) | The control loop that turns a single model call into a multi-turn, tool-using agent. |
| 04 | [Deterministic Override](patterns/04-deterministic-override/) | Move a must-always-hold rule out of the prompt and into a code hook that intercepts a tool call before it executes. |
| 05 | [Tool Gate](patterns/05-tool-gate/) | Enforce required ordering between tool calls by tracking, in code, which prerequisites have already succeeded. |
| 06 | [Validation-Retry Loop](patterns/06-validation-retry-loop/) | Validate structured output against richer business rules than a schema can express, and feed the error back for a bounded retry. |
| 07 | [Structured Error Classification](patterns/07-structured-error-classification/) | Replace error strings with a structured error object (`errorCategory`, `isRetryable`, `message`) so recovery behavior is deterministic. |
| 08 | [Confidence-Based Routing](patterns/08-confidence-based-routing/) | Attach a coarse, named confidence category to each output and route low-confidence results to review. |
| 09 | [Review Pass](patterns/09-review-pass/) | Add a second pass that judges a draft against an explicit binary rubric before it ships. |
| 10 | [Coordinator-Subagent Hierarchy](patterns/10-coordinator-subagent-hierarchy/) | Decompose a large task into a coordinator that dispatches narrow subagents in parallel and merges their structured results. |

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

## Relationship to the whitepaper

The two-digit prefix on each pattern directory (`03`–`10`) matches the chapter
numbering in the whitepaper, so `patterns/05-tool-gate/` is Chapter 5. Chapters 1 and 2
(introduction and the pattern template) and Chapter 11 (closing) are prose-only, and
the **smaller "appendix" patterns** in the paper (Tool Description Disambiguation,
Session Facts, Parallel Execution, and the rest) are described inline there and do not
ship as standalone code here.

## License

Sample/illustrative code, provided **as-is** under the [MIT License](LICENSE). See the
whitepaper for the full prescriptive guidance.

This is sample code, for non-production usage. You should work with your security and
legal teams to meet your organizational security, regulatory, and compliance
requirements before deployment.
