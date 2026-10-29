EVALUATION_CHECKLIST = """
Review the draft response against this checklist. For each item, answer Yes/No:

1. All concerns addressed: Does the response address every issue the customer raised?
2. Errors explained: Are all error outcomes explained in plain language?
3. Specific details: Are transaction IDs, amounts, and refund references present?
4. Next steps clear: Does the response tell the customer what to do next?
5. No raw JSON: Is the response free of raw JSON, error codes, or internal identifiers?

If any item is No, revise the response to address the deficiency.
Return ONLY the final (possibly revised) response text.
"""

def run_agent_with_self_eval(user_message: str) -> str:
    draft = run_agent(user_message)   # primary pass (Agentic Loop)

    eval_response = client.messages.create(
        model="global.anthropic.claude-opus-4-8",
        max_tokens=4096,
        system=EVALUATION_CHECKLIST,
        messages=[{
            "role": "user",
            "content": (f"Original customer message:\n{user_message}\n\n"
                        f"Draft response:\n{draft}"),
        }],
    )
    return eval_response.content[0].text
