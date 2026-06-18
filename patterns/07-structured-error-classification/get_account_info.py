def get_account_info(account_id: str) -> str:
    if account_id not in accounts:
        return tool_error(
            "validation", False,
            f"Account '{account_id}' does not exist. Ask the customer to verify "
            f"their account number.",
        )
    account = accounts[account_id]
    if account["status"] == "frozen":
        return tool_error(
            "permission", False,
            f"Account {account_id} is frozen. Refund operations are not permitted.",
        )
    return json.dumps(account)
