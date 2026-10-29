from claude_agent_sdk import AgentDefinition

WEB_SEARCH_AGENT = AgentDefinition(
    model="haiku",                      # cheaper model, narrow task
    description=(
        "Searches the web for factual information. Returns structured findings "
        "with source URLs, publication dates, and confidence scores."
    ),
    prompt="""
HARD LIMITS — do NOT exceed:
- 1 WebSearch call
- 2 WebFetch calls
- Then STOP and return JSON immediately

Return ONLY this JSON:
{
  "findings": [{
    "claim": "...", "evidence": "...",
    "source_url": "...", "source_name": "...",
    "publication_date": "YYYY-MM-DD or null",
    "confidence": 0.0-1.0,
    "source_type": "academic|news|documentation|blog|other",
    "source_type_detail": null
  }],
  "gaps": ["Topics I could not find reliable information on"]
}
""",
    tools=["WebSearch", "WebFetch"],
)
