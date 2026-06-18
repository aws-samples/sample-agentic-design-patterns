from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def run_research_pipeline(question: str) -> dict:
    final_result = None
    async for message in query(
        prompt=f"Research this question: {question}",
        options=ClaudeAgentOptions(
            system_prompt=COORDINATOR_SYSTEM,
            # dontAsk + allowlist: only these tools run; everything else is denied (not approved).
            permission_mode="dontAsk",
            allowed_tools=["Task", "Read", "Glob"],
            agents={
                "web-search-agent": WEB_SEARCH_AGENT,
                "doc-analysis-agent": DOC_ANALYSIS_AGENT,
            },
            max_turns=10,
        ),
    ):
        if isinstance(message, ResultMessage):
            final_result = json.loads(message.result)
    return final_result
