def extract_with_retry(document: str, max_retries: int = 2) -> SubagentResult | None:
    raw = extract_once(document)

    for attempt in range(max_retries + 1):
        try:
            return SubagentResult(**raw)
        except ValidationError as e:
            if attempt == max_retries:
                return None  # exhausted; surface upstream

            retry = client.messages.create(
                model="global.anthropic.claude-opus-4-8",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=[EXTRACTION_TOOL],
                tool_choice={"type": "tool", "name": "extract_research_findings"},
                messages=[
                    {"role": "user",
                     "content": f"Extract findings from:\n\n{document}"},
                    {"role": "assistant",
                     "content": [{"type": "tool_use",
                                  "id": "prev_extraction",
                                  "name": "extract_research_findings",
                                  "input": raw}]},
                    {"role": "user",
                     "content": [{"type": "tool_result",
                                  "tool_use_id": "prev_extraction",
                                  "content": (f"Your previous extraction failed "
                                              f"validation with these errors:\n{e}\n\n"
                                              f"Please re-extract, correcting only "
                                              f"the fields mentioned."),
                                  "is_error": True}]},
                ],
            )
            raw = retry.content[0].input

    return None
