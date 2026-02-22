# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


from typing import Any


def truncate_base64_in_dict(d: Any, min_length: int = 100) -> Any:
    """
    Recursively truncate base64 data in any dict structure for debug printing.

    Looks for common base64 field names across all API formats:
    - Google: inlineData.data
    - OpenAI: image.data, data
    - Anthropic: source.data
    - Generic: base64_data, base64, data (if looks like base64)

    Args:
        d: The dict/list/value to process
        min_length: Minimum string length to consider for truncation (default 100)

    Returns:
        A copy with base64 data truncated to "<N chars>" format

    Example:
        >>> payload = message.to_google_content()
        >>> print(truncate_base64_in_dict(payload))  # Safe for debug output
    """
    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            # Known base64 field names
            if (
                key in ("data", "base64_data", "base64")
                and isinstance(value, str)
                and len(value) > min_length
            ):
                # Check if it looks like base64 (alphanumeric + /+=)
                if all(c.isalnum() or c in "/+=" for c in value[:100]):
                    result[key] = f"<{len(value)} chars>"
                else:
                    result[key] = value
            else:
                result[key] = truncate_base64_in_dict(value, min_length)
        return result
    elif isinstance(d, list):
        return [truncate_base64_in_dict(item, min_length) for item in d]
    else:
        return d
