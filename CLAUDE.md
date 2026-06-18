# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Companion code for the AWS Prescriptive Guidance whitepaper *Agentic Design Patterns*. The repo holds runnable Python for the eight larger patterns (whitepaper Chapters 3–10), one directory per pattern under `patterns/NN-name/`, each with its own `README.md` that distills the corresponding chapter.

These are **illustrative fragments**, not a turn-key application. Snippets reference helpers the whitepaper defines in surrounding prose or in the source workshop (`SYSTEM_PROMPT`, `TOOLS`, `execute_tool(...)`, `lookup_transaction_amount(...)`, per-pattern tool implementations) that are not defined here. The code is meant to be read against the prose, not run as a whole system.

## Companion repo (source of truth)

This repo is downstream of the whitepaper repo, a sibling directory at `../agentic-design-patterns-whitepaper` (both live under `~/code/`). The whitepaper's `site/index.html` is the canonical source: every code file here is extracted **verbatim** from a `<pre>` code block in that file, and each pattern `README.md` summarizes that chapter's narrative.

There is no shared build or submodule; the two repos are kept in sync by hand. When code or wording changes:

- A pattern's `*.py` should match the corresponding `<pre>` block in `site/index.html`. If they diverge, the whitepaper wins — update the code here to match, not the other way around.
- A pattern's `README.md` here is a distillation, so reword it only when the chapter's substance changes, and keep it consistent with the whitepaper text.
- The directory prefix is the chapter number (`patterns/05-tool-gate/` is Ch. 5). Chapters 1–2 and 11 are prose-only, and the twelve smaller appendix patterns live only in the whitepaper, so they have no code here.

## Layout

```
patterns/NN-name/    one directory per larger pattern (03–10)
  README.md          distills the whitepaper chapter; says which file to open first
  *.py               the extracted code, read in the order the README gives
requirements.txt     Anthropic SDK + Pydantic
```

## Conventions

- The code targets the **Anthropic Python SDK against Amazon Bedrock** (`from anthropic import AnthropicBedrock`); the Validation-Retry Loop also uses Pydantic. Snippets reference model id `global.anthropic.claude-opus-4-8` — swap in whichever Claude model id is enabled for your Bedrock account.
- Running anything needs Bedrock access and AWS credentials from the standard chain (`AWS_PROFILE`, `AWS_REGION`, env vars, or an instance role).
- Keep snippets verbatim with the whitepaper. Prefer fixing the whitepaper and re-extracting over editing only this repo, so the two never drift.
- Each pattern `README.md` names the file to read first; preserve that reading order when adding or editing files.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
