"""
Centralized error handling for AI provider APIs.
"""

from dataclasses import dataclass

# Status codes that are always retryable — server-side transient failures.
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504, 529}

# Status codes that are never retryable — client errors, auth failures, etc.
_NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404, 422}


@dataclass
class RetryableError:
    error_type: str
    message: str
    status_code: int | None = None
    retry_after: float | None = None
    is_retryable: bool = True
    user_message: str = "The AI service is temporarily unavailable. Retrying..."

    def get_backoff_delay(self, attempt: int) -> float:
        if self.retry_after:
            return self.retry_after
        return min(2 ** attempt, 30)


def _extract_status_code(exception: Exception) -> int | None:
    """Pull the HTTP status code off an exception using the most common SDK attributes."""
    for attr in ("status_code", "code", "http_status", "status"):
        val = getattr(exception, attr, None)
        if isinstance(val, int):
            return val
    return None


def _retry_after_from_status(status_code: int) -> float:
    if status_code == 429:
        return 10.0
    if status_code in (502, 503, 504):
        return 5.0
    return 3.0


def _classify_by_status(status_code: int, provider: str, message: str) -> RetryableError:
    if status_code in _NON_RETRYABLE_STATUS_CODES:
        return RetryableError(
            error_type="client_error",
            message=message,
            status_code=status_code,
            is_retryable=False,
            user_message="The request was rejected by the AI service. Please check your input.",
        )
    if status_code in _RETRYABLE_STATUS_CODES:
        if status_code == 429:
            return RetryableError(
                error_type="rate_limit",
                message=f"{provider} rate limit exceeded",
                status_code=status_code,
                retry_after=10.0,
                is_retryable=True,
                user_message="Rate limit reached. Retrying shortly...",
            )
        return RetryableError(
            error_type="server_error",
            message=f"{provider} server error ({status_code})",
            status_code=status_code,
            retry_after=_retry_after_from_status(status_code),
            is_retryable=True,
            user_message="The AI service is temporarily unavailable. Retrying...",
        )
    # Unknown status code — default to retryable so we don't silently drop errors.
    return RetryableError(
        error_type="unknown_server_error",
        message=message,
        status_code=status_code,
        retry_after=3.0,
        is_retryable=True,
        user_message="An unexpected error occurred. Retrying...",
    )


def _fallback_classify(error_str: str, provider: str) -> RetryableError:
    """
    Last-resort string-based classification when no status code is available.
    Defaults to retryable for anything that looks like a server-side problem,
    and only marks non-retryable for clear client errors.
    """
    s = error_str.lower()

    if any(x in s for x in ("401", "403", "invalid api key", "unauthorized", "forbidden")):
        return RetryableError(
            error_type="auth_error",
            message=error_str,
            is_retryable=False,
            user_message="Authentication failed. Please check your API key.",
        )
    if any(x in s for x in ("400", "invalid request", "bad request")):
        return RetryableError(
            error_type="invalid_request",
            message=error_str,
            is_retryable=False,
            user_message="The request was invalid. Please check your input.",
        )
    if any(x in s for x in ("429", "rate limit", "quota")):
        return RetryableError(
            error_type="rate_limit",
            message=error_str,
            retry_after=10.0,
            is_retryable=True,
            user_message="Rate limit reached. Retrying shortly...",
        )
    if any(x in s for x in ("timeout", "timed out", "connection", "network")):
        return RetryableError(
            error_type="network_error",
            message=error_str,
            retry_after=2.0,
            is_retryable=True,
            user_message="Network connection issue. Retrying...",
        )

    # Everything else — server error, overloaded, unavailable, unknown — retry it.
    return RetryableError(
        error_type="server_error",
        message=error_str,
        retry_after=5.0,
        is_retryable=True,
        user_message="The AI service encountered an error. Retrying...",
    )


def classify_google_error(exception: Exception) -> RetryableError:
    status_code = _extract_status_code(exception)
    if status_code is not None:
        return _classify_by_status(status_code, "Google", str(exception))
    return _fallback_classify(str(exception), "Google")


def classify_openai_error(exception: Exception) -> RetryableError:
    status_code = _extract_status_code(exception)
    if status_code is not None:
        return _classify_by_status(status_code, "OpenAI", str(exception))
    return _fallback_classify(str(exception), "OpenAI")


def classify_anthropic_error(exception: Exception) -> RetryableError:
    status_code = _extract_status_code(exception)
    if status_code is not None:
        return _classify_by_status(status_code, "Anthropic", str(exception))
    return _fallback_classify(str(exception), "Anthropic")


def classify_provider_error(provider: str, exception: Exception) -> RetryableError:
    if provider == "google":
        return classify_google_error(exception)
    elif provider == "openai":
        return classify_openai_error(exception)
    elif provider == "anthropic":
        return classify_anthropic_error(exception)

    status_code = _extract_status_code(exception)
    if status_code is not None:
        return _classify_by_status(status_code, provider, str(exception))
    return _fallback_classify(str(exception), provider)
