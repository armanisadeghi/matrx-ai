"""
Protocol definition for stream handlers used in AI chat implementations.

This protocol defines the interface that all stream handlers must implement,
enabling type hints without circular import issues.
"""

from typing import Any, Dict, Optional, Protocol


class StreamHandler(Protocol):
    """
    Protocol for stream handlers that emit events during AI chat responses.
    
    Multiple implementations can conform to this protocol:
    - FastAPIResponseEmitter (for HTTP streaming)
    - SocketEmitter (for WebSocket streaming)
    - Any custom implementation
    
    Using Protocol allows structural typing without import dependencies.
    """

    async def send_chunk(self, chunk: str) -> None:
        """
        Send a text chunk to the client.
        
        Args:
            chunk: Text content to stream (can be partial text)
        """
        ...

    async def send_chunk_final(self, chunk: str) -> None:
        """
        Send final chunk and end the stream.
        
        Args:
            chunk: Final text content
        """
        ...

    async def send_status_update(
        self,
        status: str,
        system_message: Optional[str] = None,
        user_visible_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send a status update event.
        
        Args:
            status: Status identifier (e.g., "processing", "complete")
            system_message: Internal message for logging/debugging
            user_visible_message: Message to display to end user
            metadata: Additional structured data
        """
        ...

    async def send_data(self, data: Any) -> None:
        """
        Send arbitrary structured data.
        
        Args:
            data: Any JSON-serializable data
        """
        ...

    async def send_data_final(self, data: Any) -> None:
        """
        Send final data and end the stream.
        
        Args:
            data: Final data payload
        """
        ...

    async def send_error(
        self,
        error_type: str,
        message: str,
        user_visible_message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send an error event.
        
        Args:
            error_type: Error type identifier
            message: Technical error message
            user_visible_message: User-friendly error message
            code: Optional error code
            details: Additional error details
        """
        ...

    async def send_end(self) -> None:
        """Signal the end of the stream."""
        ...

    async def fatal_error(
        self,
        error_type: str,
        message: str,
        user_visible_message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send a fatal error and end the stream.
        
        Args:
            error_type: Error type identifier
            message: Technical error message
            user_visible_message: User-friendly error message
            code: Optional error code
            details: Additional error details
        """
        ...

    async def send_cancelled(self) -> None:
        """Send a cancellation notification and end the stream."""
        ...

    async def send_function_call(
        self,
        user_visible_message: str,
        call_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        mcp_input: Optional[dict] = None,
        mcp_output: Optional[dict] = None,
        step_data: Optional[dict] = None,
        mcp_error: Optional[str] = None,
    ) -> None:
        """
        Send a tool/function call update event.
        
        Args:
            user_visible_message: Message to display to user
            call_id: Unique identifier for this call
            tool_name: Name of the tool being called
            mcp_input: MCP tool input data
            mcp_output: MCP tool output data
            step_data: Additional step information
            mcp_error: Error message if call failed
        """
        ...

    async def send_tool_event(
        self,
        event_data: dict,
    ) -> None:
        """
        Send a structured tool event to the client.

        The event_data dict is the exact ToolStreamEvent shape:
          event, call_id, tool_name, timestamp, message, show_spinner, data

        This replaces send_function_call() for the new tool system.
        One level of nesting, explicit event type, no type-inference.
        """
        ...

    async def send_text_chunk(self, text: str) -> None:
        """
        Legacy method: Send a text chunk (alias for send_chunk).
        
        Args:
            text: Text content to stream
        """
        ...

    async def send_info(self, info: Any) -> None:
        """
        Send an informational event.
        
        Args:
            info: Information payload
        """
        ...

