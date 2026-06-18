import json

def tool_error(category: str, is_retryable: bool, message: str) -> str:
    return json.dumps({
        "error": True,
        "errorCategory": category,
        "isRetryable": is_retryable,
        "message": message,
    })
