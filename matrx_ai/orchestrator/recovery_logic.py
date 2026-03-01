from typing import Literal

from matrx_utils import vcprint

from matrx_ai.config.finish_reason import FinishReason
from matrx_ai.config.unified_config import (
    UnifiedResponse,
)
from matrx_ai.orchestrator.requests import AIMatrixRequest


def handle_finish_reason(
    response: UnifiedResponse,
    request: AIMatrixRequest,
    retry_attempt: int,
    max_retries: int,
    debug: bool = False,
) -> Literal["continue", "retry", "stop"]:
    """
    Handle finish reason and prepare for retry if needed.
    
    This function:
    - Checks the finish reason from the response
    - Logs appropriate information
    - For retryable errors, adds context to the request for retry
    - Returns action: "continue", "retry", or "stop"
    
    Returns:
        - "continue": Finish reason is OK, proceed with normal flow
        - "retry": Retryable error prepared, retry the request
        - "stop": Fatal error, stop execution
    """
    finish_reason = response.finish_reason
    
    # No finish reason, assume success
    if not finish_reason:
        return "continue"
    
    # Convert string to FinishReason enum if needed
    if isinstance(finish_reason, str):
        try:
            finish_reason = FinishReason(finish_reason)
        except ValueError:
            vcprint(f"⚠️  Unknown finish reason '{finish_reason}', continuing anyway", color="yellow")
            return "continue"
    
    # Success case - continue normally
    if finish_reason.is_success():
        return "continue"
    
    # Log non-success finish reason
    vcprint(f"\n⚠️  Non-success finish reason: {finish_reason}", color="yellow")
    vcprint(
        response.raw_response,
        f"Full Response (finish_reason={finish_reason})",
        color="yellow",
        verbose=True
    )
    
    # Check if retryable
    if finish_reason.is_retryable():
        if retry_attempt < max_retries:
            vcprint(
                f"↻ Retry {retry_attempt + 1}/{max_retries} due to {finish_reason}",
                color="cyan"
            )
            
            # Add the failed response to conversation history
            # This ensures the model sees what it tried to do
            for msg in response.messages:
                request.config.messages.append(msg)
            
            # Build helpful message about available tools
            if request.config.tools:
                tool_names = [tool if isinstance(tool, str) else tool.get('name', 'unknown') 
                             for tool in request.config.tools]
                tools_message = f"The previous function call failed. The following tools are the only ones available: {tool_names}. Please use only these tools. If you do not have the resources you need, do not guess. Inform the user and avoid further complication."
            else:
                tools_message = "The previous function call failed. No tools/functions are available in this conversation. Please respond directly without attempting to call any functions. If you do not have the resources you need, do not guess. Inform the user and avoid further complication."
            
            # Append user message to config
            request.config.append_user_message(tools_message)
            
            vcprint(f"📝 Added retry context: {tools_message}", color="cyan", verbose=debug)
            
            return "retry"
        else:
            vcprint(
                f"✗ Max retries ({max_retries}) exceeded for {finish_reason}",
                color="red"
            )
            # Fall through to error handling
    
    # Check if it's an error
    if finish_reason.is_error():
        vcprint(
            f"✗ Stopping execution due to error finish reason: {finish_reason}",
            color="red"
        )
        return "stop"
    
    # Unknown case - continue cautiously
    vcprint(
        f"⚠️  Unhandled finish reason '{finish_reason}', continuing anyway",
        color="yellow"
    )
    return "continue"

