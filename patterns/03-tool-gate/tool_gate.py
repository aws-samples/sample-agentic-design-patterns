import json

class ToolGate:
    _prerequisites: dict[str, list[str]] = {
        "get_transactions":         ["get_account_info"],
        "check_refund_eligibility": ["get_account_info", "get_transactions"],
        "process_refund":           ["get_account_info", "check_refund_eligibility"],
    }

    def __init__(self) -> None:
        self._satisfied: set[str] = set()

    def check(self, tool_name: str) -> str | None:
        missing = [p for p in self._prerequisites.get(tool_name, [])
                   if p not in self._satisfied]
        if missing:
            return (f"Cannot call '{tool_name}': the following tools must "
                    f"succeed first: " + ", ".join(f"'{m}'" for m in missing))
        return None

    def mark_succeeded(self, tool_name: str, result_json: str) -> None:
        try:
            data = json.loads(result_json)
            if not data.get("error", False):
                self._satisfied.add(tool_name)
        except (json.JSONDecodeError, AttributeError):
            pass  # fail closed: an unparseable result does not satisfy a prerequisite
