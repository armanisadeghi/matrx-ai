import os
import asyncio
import traceback
import json
from typing import Dict, Any
from matrx_utils import vcprint
from together import AsyncTogether
from config.unified_config import (
    UnifiedConfig,
    UnifiedResponse,
    UnifiedMessage,
    TextContent,
    ToolCallContent,
)
from config.finish_reason import FinishReason
from client.translators import TogetherTranslator
from client.usage import TokenUsage
from context.emitter_protocol import Emitter

DEBUG_OVERRIDE = False


class TogetherChat:
    """Together AI API-specific endpoint implementation (OpenAI-style)."""

    client: AsyncTogether
    endpoint_name: str
    debug: bool

    def __init__(self, debug: bool = False):
        self.client = AsyncTogether(api_key=os.environ.get("TOGETHER_API_KEY"))
        self.endpoint_name = "[TOGETHER CHAT]"
        self.translator = TogetherTranslator()
        self.debug = debug

        if DEBUG_OVERRIDE:
            self.debug = True

    def to_provider_config(
        self, config: UnifiedConfig, api_class: str
    ) -> Dict[str, Any]:
        return self.translator.to_together(config)

    def to_unified_response(
        self, response: Any, model: str = ""
    ) -> UnifiedResponse:
        """Convert Together response to unified format"""
        return self.translator.from_together(response)

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from context.app_context import get_app_context
        emitter = get_app_context().emitter

        self.debug = debug

        # Build provider-specific config
        config_data = self.to_provider_config(unified_config, api_class)
        
        vcprint(config_data, "Together API Config Data", color="blue", verbose=debug)
        
        try:
            # Translator sets stream correctly
            if config_data.get("stream", False):
                return await self._execute_streaming(
                    config_data, emitter, unified_config.model
                )
            else:
                return await self._execute_non_streaming(
                    config_data, emitter, unified_config.model
                )

        except Exception as e:
            # Import here to avoid circular dependency
            from client.errors import classify_provider_error
            
            # Classify the error to determine if it's retryable
            error_info = classify_provider_error("together", e)
            
            await emitter.send_error(
                error_type=error_info.error_type,
                message=error_info.message,
                user_message=error_info.user_message,
            )
            vcprint(e, "[Together Chat] Error", color="red")
            traceback.print_exc()
            
            # Re-raise with error classification attached
            e.error_info = error_info
            raise

    async def _execute_non_streaming(
        self,
        config_data: Dict[str, Any],
        emitter: Emitter,
        model: str,
    ) -> UnifiedResponse:
        """Execute non-streaming Together request"""

        vcprint("[Together] Starting API call (non-streaming)...", color="cyan")
        
        # Native async API call
        response = await self.client.chat.completions.create(**config_data)

        vcprint("[Together] API call completed, processing response...", color="cyan")
        vcprint(response, "Together Response", color="green", verbose=self.debug)

        # Convert to unified format first
        vcprint("[Together] Converting to unified format...", color="cyan")
        converted_response = self.to_unified_response(response, model)
        vcprint(f"[Together] Conversion complete. {len(converted_response.messages)} messages", color="cyan")

        # Send content through emitter
        vcprint("[Together] Sending content to stream handler...", color="cyan")
        for message in converted_response.messages:
            for content in message.content:
                if isinstance(content, TextContent):
                    await emitter.send_chunk(content.text)
                elif isinstance(content, ToolCallContent):
                    await emitter.send_status_update(
                        status="processing",
                        system_message=f"Executing {content.name}",
                        user_message=f"Using tool {content.name}",
                        metadata={"tool_call": content.name},
                    )

        vcprint("[Together] Non-streaming execution completed successfully", color="green")
        return converted_response

    async def _execute_streaming(
        self,
        config_data: Dict[str, Any],
        emitter: Emitter,
        model: str,
    ) -> UnifiedResponse:
        """Execute streaming Together request"""

        vcprint("[Together] Starting API call (streaming)...", color="cyan")
        
        # Native async streaming
        stream = await self.client.chat.completions.create(**config_data)
        
        vcprint("[Together] Stream connection established, processing chunks...", color="cyan")

        # Accumulate response data for final unified response
        accumulated_content = ""
        accumulated_tool_calls = []
        usage_data = None
        finish_reason = None
        response_id = None

        # Process stream chunks
        async for chunk in stream:
            response_id = chunk.id
            
            # vcprint(chunk, "Together Stream Chunk", color="magenta")
            
            # Capture usage from final chunk (can come without choices)
            if chunk.usage:
                usage_data = chunk.usage
            
            # Only process choice-specific data if choices exist
            if not chunk.choices:
                continue
                
            choice = chunk.choices[0]
            delta = choice.delta
            
            # Handle content chunks
            if delta.content:
                accumulated_content += delta.content
                await emitter.send_chunk(delta.content)
                await asyncio.sleep(0)

            # Handle tool calls - Together API doesn't always include this field
            # Together can return tool_calls as dicts or objects
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                if self.debug:
                    vcprint(delta, "Together Tool Calls", color="magenta")
                for tc in delta.tool_calls:
                    # Handle both dict and object formats
                    tc_index = tc.get("index") if isinstance(tc, dict) else getattr(tc, "index", None)
                    tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                    tc_func = tc.get("function") if isinstance(tc, dict) else getattr(tc, "function", None)
                    
                    if tc_index is None:
                        continue
                        
                    while len(accumulated_tool_calls) <= tc_index:
                        accumulated_tool_calls.append({
                            "id": "",
                            "name": "",
                            "arguments": ""
                        })
                    
                    if tc_id:
                        accumulated_tool_calls[tc_index]["id"] = tc_id
                    
                    if tc_func:
                        # Function can also be dict or object
                        func_name = tc_func.get("name") if isinstance(tc_func, dict) else getattr(tc_func, "name", None)
                        func_args = tc_func.get("arguments") if isinstance(tc_func, dict) else getattr(tc_func, "arguments", None)
                        
                        if func_name:
                            accumulated_tool_calls[tc_index]["name"] = func_name
                        if func_args:
                            # Arguments might be a dict or string
                            if isinstance(func_args, dict):
                                accumulated_tool_calls[tc_index]["arguments"] = json.dumps(func_args)
                            else:
                                accumulated_tool_calls[tc_index]["arguments"] += func_args

            # Capture finish reason
            if choice.finish_reason:
                finish_reason = choice.finish_reason

        # Build unified response from accumulated data
        content = []
        
        if accumulated_content:
            content.append(TextContent(text=accumulated_content))
        
        for tc_data in accumulated_tool_calls:
            if tc_data["name"]:
                arguments = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                content.append(
                    ToolCallContent(
                        id=tc_data["id"],
                        name=tc_data["name"],
                        arguments=arguments
                    )
                )

        messages = []
        if content:
            messages.append(
                UnifiedMessage(
                    role="assistant",
                    content=content,
                    id=response_id
                )
            )

        # Convert usage to TokenUsage
        token_usage = None
        if usage_data:
            token_usage = TokenUsage(
                input_tokens=usage_data.prompt_tokens,
                output_tokens=usage_data.completion_tokens,
                matrx_model_name=model,
                provider_model_name=model,
                api="together",
                response_id=response_id or ""
            )

        # Map finish_reason to unified format
        unified_finish_reason = None
        if finish_reason == "stop":
            unified_finish_reason = FinishReason.STOP
        elif finish_reason == "length":
            unified_finish_reason = FinishReason.MAX_TOKENS
        elif finish_reason == "tool_calls":
            unified_finish_reason = FinishReason.TOOL_CALLS
        elif finish_reason == "content_filter":
            unified_finish_reason = FinishReason.CONTENT_FILTER

        vcprint("[Together] Streaming execution completed successfully", color="green")

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=unified_finish_reason,
            stop_reason=finish_reason,
        )

