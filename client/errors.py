"""
Centralized error handling for AI provider APIs.

This module defines error types and retry strategies for all AI providers.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class RetryableError:
    """Represents an error that can be retried with backoff."""
    
    error_type: str
    message: str
    status_code: Optional[int] = None
    retry_after: Optional[float] = None
    is_retryable: bool = True
    user_message: str = "The AI service is temporarily unavailable. Retrying..."
    
    def get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay in seconds."""
        if self.retry_after:
            return self.retry_after
        
        # Exponential backoff: 2^attempt seconds (1s, 2s, 4s, 8s, ...)
        return min(2 ** attempt, 30)  # Cap at 30 seconds


def classify_google_error(exception: Exception) -> RetryableError:
    """
    Classify Google API errors and determine retry strategy.
    
    Args:
        exception: The exception raised by Google API
        
    Returns:
        RetryableError with classification and retry strategy
    """
    error_str = str(exception)
    
    # Check for 503 Service Unavailable (high demand)
    if "503" in error_str and "high demand" in error_str.lower():
        return RetryableError(
            error_type="rate_limit_high_demand",
            message="Google API is experiencing high demand",
            status_code=503,
            retry_after=5.0,  # Wait 5 seconds before retry
            is_retryable=True,
            user_message="The AI model is experiencing high demand. Retrying in a moment..."
        )
    
    # Check for 429 Rate Limit
    if "429" in error_str or "rate limit" in error_str.lower():
        return RetryableError(
            error_type="rate_limit",
            message="Google API rate limit exceeded",
            status_code=429,
            retry_after=10.0,  # Wait 10 seconds for rate limits
            is_retryable=True,
            user_message="Rate limit reached. Retrying shortly..."
        )
    
    # Check for 500 Internal Server Error
    if "500" in error_str:
        return RetryableError(
            error_type="server_error",
            message="Google API internal server error",
            status_code=500,
            retry_after=3.0,
            is_retryable=True,
            user_message="The AI service encountered an error. Retrying..."
        )
    
    # Check for network/timeout errors
    if any(keyword in error_str.lower() for keyword in ["timeout", "connection", "network"]):
        return RetryableError(
            error_type="network_error",
            message="Network or timeout error",
            status_code=None,
            retry_after=2.0,
            is_retryable=True,
            user_message="Network connection issue. Retrying..."
        )
    
    # Non-retryable error (400, 401, 403, etc.)
    return RetryableError(
        error_type="non_retryable",
        message=error_str,
        status_code=None,
        is_retryable=False,
        user_message="The AI service returned an error. Please check your request and try again."
    )


def classify_openai_error(exception: Exception) -> RetryableError:
    """Classify OpenAI API errors."""
    error_str = str(exception)
    
    if "rate_limit" in error_str.lower() or "429" in error_str:
        return RetryableError(
            error_type="rate_limit",
            message="OpenAI rate limit exceeded",
            status_code=429,
            retry_after=10.0,
            is_retryable=True,
            user_message="Rate limit reached. Retrying shortly..."
        )
    
    if "503" in error_str or "502" in error_str or "500" in error_str:
        return RetryableError(
            error_type="server_error",
            message="OpenAI server error",
            status_code=int(error_str.split()[0]) if error_str[0].isdigit() else 500,
            retry_after=3.0,
            is_retryable=True,
            user_message="The AI service encountered an error. Retrying..."
        )
    
    return RetryableError(
        error_type="non_retryable",
        message=error_str,
        is_retryable=False,
        user_message="The AI service returned an error. Please check your request and try again."
    )


def classify_anthropic_error(exception: Exception) -> RetryableError:
    """Classify Anthropic API errors."""
    error_str = str(exception)
    
    if "overloaded" in error_str.lower() or "529" in error_str:
        return RetryableError(
            error_type="overloaded",
            message="Anthropic API is overloaded",
            status_code=529,
            retry_after=5.0,
            is_retryable=True,
            user_message="The AI model is overloaded. Retrying in a moment..."
        )
    
    if "rate_limit" in error_str.lower() or "429" in error_str:
        return RetryableError(
            error_type="rate_limit",
            message="Anthropic rate limit exceeded",
            status_code=429,
            retry_after=10.0,
            is_retryable=True,
            user_message="Rate limit reached. Retrying shortly..."
        )
    
    return RetryableError(
        error_type="non_retryable",
        message=error_str,
        is_retryable=False,
        user_message="The AI service returned an error. Please check your request and try again."
    )


def classify_provider_error(provider: str, exception: Exception) -> RetryableError:
    """
    Classify errors from any provider.
    
    Args:
        provider: Provider name (google, openai, anthropic, etc.)
        exception: The exception raised
        
    Returns:
        RetryableError with classification and retry strategy
    """
    if provider == "google":
        return classify_google_error(exception)
    elif provider == "openai":
        return classify_openai_error(exception)
    elif provider == "anthropic":
        return classify_anthropic_error(exception)
    else:
        # Generic classification for other providers
        error_str = str(exception)
        
        # Check for common retryable patterns
        if any(keyword in error_str.lower() for keyword in ["503", "502", "500", "timeout", "overload"]):
            return RetryableError(
                error_type="server_error",
                message=error_str,
                retry_after=3.0,
                is_retryable=True,
                user_message="The AI service encountered an error. Retrying..."
            )
        
        return RetryableError(
            error_type="unknown",
            message=error_str,
            is_retryable=False,
            user_message="An unexpected error occurred. Please try again."
        )
