ESCALATION_THRESHOLD = 500.00

def apply_pre_tool_hook(tool_name: str, tool_input: dict) -> dict | None:
    if tool_name == "process_refund":
        # Do NOT trust the model's amount. Look it up.
        amount = lookup_transaction_amount(tool_input["transaction_id"])
        if amount > ESCALATION_THRESHOLD:
            return {
                "escalated": True,
                "ticket_id": f"ESC-{tool_input['transaction_id']}",
                "message": (
                    f"This refund of ${amount:.2f} exceeds the automated limit. "
                    f"A specialist will review within 2 business hours."
                ),
            }
    return None  # allow the call to proceed
