from config.unified_config import (
    CodeExecutionContent,
    CodeExecutionResultContent,
    UnifiedConfig,
)
from typing import Dict, Any, TypedDict, List, Optional
from openai.types.responses import Response as OpenAIResponse
from config.unified_config import UnifiedResponse, UnifiedMessage
from config.finish_reason import FinishReason
from client.usage import TokenUsage
from client.thinking_config import ThinkingConfig
from matrx_utils import vcprint
import json
from google.genai.types import (
    Content,
    GenerateContentConfig,
    GenerateContentResponse,
    Part,
)
from google.genai import types
from config.unified_config import (
    ToolResultContent,
    TextContent,
    ToolCallContent,
    YouTubeVideoContent,
    ThinkingContent,
    ImageContent,
    AudioContent,
    VideoContent,
    DocumentContent,
)
from tools.registry import ToolRegistryV2
import rich


# ============================================================================
# TRANSLATORS FOR ALL PROVIDERS: OpenAI, Anthropic, Cerebras, Together, Groq, XAI, Google
# ============================================================================


# ============================================================================
# OPENAI TRANSLATOR
# ============================================================================


class OpenAITranslator:
    """Translates between unified format and OpenAI Responses API"""

    def to_openai(self, config: UnifiedConfig, api_class: str) -> Dict[str, Any]:

        """
        Convert unified config to OpenAI Responses API format.
        
        Creates developer message from config.system_instruction.
        Delegates message conversion to UnifiedMessage.to_openai_items().
        """
        messages = []
        include_items = []
        
        rich.print(config)

        # Add developer message from system_instruction if present
        if config.system_instruction:
            messages.append(
                {
                    "role": "developer",
                    "content": [
                        {"type": "input_text", "text": config.system_instruction}
                    ],
                }
            )

        # Process all messages - delegate to message method
        for msg in config.messages:
            converted = msg.to_openai_items()
            rich.print(converted)

            if converted:
                # If it's a list (OUTPUT/TOOL role), extend messages with all items
                if isinstance(converted, list):
                    messages.extend(converted)
                # Otherwise it's a single wrapped message, append it
                else:
                    messages.append(converted)

        # Build request
        openai_request = {"model": config.model, "input": messages}

        tools = []
        if config.tools:
            tools.extend(ToolRegistryV2.get_instance().get_provider_tools(config.tools, "openai"))
        if config.internal_web_search:
            tools.append({"type": "web_search"})
            include_items.append("web_search_call.action.sources")

        if tools:
            openai_request["tools"] = tools

        # Add optional parameters
        if config.max_output_tokens:
            openai_request["max_output_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            openai_request["temperature"] = config.temperature

        if config.top_p is not None:
            if api_class == "openai_standard":
                openai_request["top_p"] = config.top_p

        # Response format
        if config.response_format:
            if config.response_format == "text":
                openai_request["text"] = {"format": {"type": "text"}}
            elif config.response_format == "json_schema":
                openai_request["text"] = {
                    "format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": config.response_format.get("name"),
                            "schema": config.response_format.get("schema"),
                        },
                    }
                }
            elif config.response_format == "json_object":
                openai_request["text"] = {
                    "format": {
                        "type": "json_object",
                        "json_object": {
                            "name": config.response_format.get("name"),
                            "schema": config.response_format.get("schema"),
                        },
                    }
                }
            else:
                vcprint(
                    config.response_format,
                    "WARNING: Unknown response format type",
                    color="red",
                )
                openai_request["text"] = {"format": {"type": "text"}}

        # Tool choice
        if config.tool_choice:
            openai_request["tool_choice"] = config.tool_choice

        # Parallel tool calls
        if not config.parallel_tool_calls:
            openai_request["parallel_tool_calls"] = False

        # Stream - Stream is not included in the request and is handled be the execution logic
        # if config.stream:
        #     openai_request["stream"] = True

        thinking = ThinkingConfig.from_settings(config)
        if api_class == "openai_reasoning" and thinking:
            openai_request["reasoning"] = thinking.to_openai_reasoning()
            include_items.append("reasoning.encrypted_content")

        if include_items:
            openai_request["include"] = include_items

        return openai_request

    def from_openai(self, response: OpenAIResponse) -> UnifiedResponse:
        """
        Convert OpenAI Responses API response to unified format.

        """
        vcprint(response, "OpenAI Response", color="blue", verbose=False)
        
        # messages = self._from_openai_messages(response.output)
        messages = []
        for item in response.output:
            messages.append(UnifiedMessage.from_openai_item(item))

        # Convert usage to TokenUsage if present
        token_usage = TokenUsage.from_openai(
            response.usage, matrx_model_name=matrx_model_name, provider_model_name=response.model, response_id=response.id
        )

        # # Map OpenAI status/finish_reason to unified format
        finish_reason = None

        if response.status == "completed":
            # If there are tool calls, set finish reason to TOOL_CALLS
            finish_reason = FinishReason.STOP
        elif response.status == "incomplete":
            finish_reason = FinishReason.MAX_TOKENS
        elif response.status == "failed":
            finish_reason = FinishReason.ERROR

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            raw_response=response,
        )


# ============================================================================
# ANTHROPIC TRANSLATOR
# ============================================================================


class AnthropicTranslator:
    """Translates between unified format and Anthropic Messages API"""

    def to_anthropic(
        self, config: UnifiedConfig, api_class: str = "anthropic_standard"
    ) -> Dict[str, Any]:
        """
        Convert unified config to Anthropic Messages API format.

        System instruction comes from config.system_instruction field.
        Delegates message conversion to UnifiedMessage.to_anthropic_blocks().

        Note: Anthropic only supports "user" and "assistant" roles.
        Tool results (role="tool") are converted to role="user".

        api_class controls which thinking path is used:
          - "anthropic_standard" / "anthropic": extended thinking (budget_tokens)
          - "anthropic_adaptive": adaptive thinking (placeholder — currently identical
            to standard; update when Anthropic stabilises the adaptive API surface)
        """
        messages = []

        for msg in config.messages:
            message_content = msg.to_anthropic_blocks()

            if message_content:
                role = "user" if msg.role == "tool" else msg.role
                messages.append({"role": role, "content": message_content})

        anthropic_request = {
            "model": config.model,
            "messages": messages,
        }

        if config.system_instruction:
            anthropic_request["system"] = config.system_instruction

        if config.tools:
            anthropic_request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(
                config.tools, "anthropic"
            )

        # Temperature / top_p mutual exclusion: Anthropic returns an error if both
        # are set on claude-opus-4-6 / claude-sonnet-4-6 (anthropic_adaptive models).
        # For safety, apply the guard on all Anthropic calls — temperature takes priority.
        if config.temperature is not None and config.top_p is not None:
            vcprint(
                f"⚠️  Anthropic requires temperature OR top_p, not both. "
                f"Dropping top_p={config.top_p} and keeping temperature={config.temperature}.",
                color="yellow",
            )
            anthropic_request["temperature"] = config.temperature
        elif config.temperature is not None:
            anthropic_request["temperature"] = config.temperature
        elif config.top_p is not None:
            anthropic_request["top_p"] = config.top_p

        if config.top_k is not None:
            anthropic_request["top_k"] = config.top_k

        if config.tool_choice:
            if config.tool_choice == "auto":
                anthropic_request["tool_choice"] = {"type": "auto"}
            elif config.tool_choice == "required":
                anthropic_request["tool_choice"] = {"type": "any"}
            elif config.tool_choice == "none":
                anthropic_request["tool_choice"] = {"type": "none"}

        thinking = ThinkingConfig.from_settings(config)
        if thinking:
            if api_class == "anthropic_adaptive":
                thinking_result = thinking.to_anthropic_adaptive_thinking(
                    current_max_tokens=config.max_output_tokens
                )
                if thinking_result:
                    anthropic_request["thinking"] = thinking_result["thinking"]
                    anthropic_request["output_config"] = thinking_result["output_config"]
                    anthropic_request["max_tokens"] = thinking_result["max_tokens"]
                else:
                    anthropic_request["max_tokens"] = (
                        config.max_output_tokens
                        if config.max_output_tokens is not None
                        else 8000
                    )
            else:
                thinking_result = thinking.to_anthropic_thinking(
                    current_max_tokens=config.max_output_tokens
                )
                if thinking_result:
                    anthropic_request["thinking"] = thinking_result["thinking"]
                    anthropic_request["max_tokens"] = thinking_result["max_tokens"]
                else:
                    anthropic_request["max_tokens"] = (
                        config.max_output_tokens
                        if config.max_output_tokens is not None
                        else 8000
                    )
        else:
            anthropic_request["max_tokens"] = (
                config.max_output_tokens
                if config.max_output_tokens is not None
                else 8000
            )

        return anthropic_request

    def from_anthropic(self, response: Dict[str, Any]) -> UnifiedResponse:
        """Convert Anthropic Messages API response to unified format"""

        message_id = response.get("id")

        message = UnifiedMessage.from_anthropic_content(
            role=response.get("role"),
            content=response.get("content", []),
            id=message_id,
        )

        # Convert usage to TokenUsage if present
        token_usage = TokenUsage.from_anthropic(
            response["usage"], matrx_model_name=matrx_model_name, response_id=message_id
        )

        finish_reason = FinishReason.from_anthropic(response.get("stop_reason"))

        return UnifiedResponse(
            messages=[message],
            usage=token_usage,
            finish_reason=finish_reason,
            raw_response=response,
        )


# ============================================================================
# CEREBRAS TRANSLATOR
# ============================================================================


class CerebrasTranslator:
    """Translates between unified format and Cerebras API (OpenAI-style)"""

    def to_cerebras(self, config: UnifiedConfig) -> Dict[str, Any]:
        """
        Convert unified config to Cerebras API format.
        
        Cerebras uses OpenAI-style messages but with some differences:
        - Uses max_completion_tokens instead of max_output_tokens
        - Tools only work in non-streaming mode
        - Supports reasoning (similar to OpenAI)
        """
        messages = []

        # Add system message if present
        if config.system_instruction:
            messages.append({"role": "system", "content": config.system_instruction})

        # Convert messages to OpenAI-style format
        for msg in config.messages:
            # Cerebras uses OpenAI-style messages with role and content
            if msg.role == "tool":
                # Tool results go as role="tool"
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": content.tool_use_id or content.call_id,
                                "content": json.dumps(content.content)
                                if isinstance(content.content, (dict, list))
                                else str(content.content),
                            }
                        )
            else:
                # Regular messages
                message_dict = {"role": msg.role, "content": ""}

                # Combine text content
                text_parts = []
                tool_calls = []

                for content in msg.content:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif isinstance(content, ToolCallContent):
                        # Tool calls are added separately
                        tool_calls.append(
                            {
                                "id": content.id,
                                "type": "function",
                                "function": {
                                    "name": content.name,
                                    "arguments": json.dumps(content.arguments),
                                },
                            }
                        )
                    elif isinstance(content, YouTubeVideoContent):
                        # YouTube URLs not supported by Cerebras - show warning
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by Cerebras models and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                # Set content
                if text_parts:
                    message_dict["content"] = "".join(text_parts)

                # Add tool_calls if present
                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                # Only add message if it has content or tool calls
                if message_dict["content"] or tool_calls:
                    messages.append(message_dict)

        # Build request
        cerebras_request = {
            "model": config.model,
            "messages": messages,
        }

        # Add optional parameters
        if config.max_output_tokens:
            cerebras_request["max_completion_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            cerebras_request["temperature"] = config.temperature
        if config.top_p is not None:
            cerebras_request["top_p"] = config.top_p

        # Stop sequences
        if config.stop_sequences:
            cerebras_request["stop"] = config.stop_sequences

        # Response format
        if config.response_format:
            cerebras_request["response_format"] = config.response_format

        # Tools - Cerebras doesn't support streaming with tools
        # If tools are present, we disable streaming at API level (system stays responsive)
        if config.tools:
            cerebras_request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(
                config.tools, "cerebras"
            )
            if config.tool_choice:
                cerebras_request["tool_choice"] = config.tool_choice

        # Stream setting - disable if tools are present
        if config.stream and not config.tools:
            cerebras_request["stream"] = True

        # Seed
        if config.seed is not None:
            cerebras_request["seed"] = config.seed

        vcprint(
            cerebras_request, "--> Cerebras Request", color="magenta", verbose=False
        )

        return cerebras_request

    def from_cerebras(self, response: Any) -> UnifiedResponse:
        """
        Convert Cerebras API response to unified format.

        Cerebras returns OpenAI-style responses:
        - response.id, response.created, response.model always present
        - response.choices is always a list with one item
        - choice.message has: content, reasoning, role, tool_calls (can be null)
        - response.usage has: prompt_tokens, completion_tokens, prompt_tokens_details
        """
        messages = []

        if not response.choices:
            vcprint(response, "Cerebras Response", color="red")
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # Extract reasoning first (if present)
        if message.reasoning:
            content.append(ThinkingContent(text=message.reasoning, provider="cerebras"))

        # Extract text content
        if message.content:
            content.append(TextContent(text=message.content))

        # Extract tool calls
        if message.tool_calls:
            for tc in message.tool_calls:
                # Parse arguments from JSON string if needed
                arguments = (
                    json.loads(tc.function.arguments)
                    if isinstance(tc.function.arguments, str)
                    else tc.function.arguments
                )
                content.append(
                    ToolCallContent(
                        id=tc.id, name=tc.function.name, arguments=arguments
                    )
                )

        # Create unified message
        if content:
            messages.append(
                UnifiedMessage(role="assistant", content=content, id=response.id)
            )

        # Convert usage to TokenUsage with cached tokens
        token_usage = None
        if response.usage:
            # Cerebras provides cached_tokens in prompt_tokens_details
            cached_tokens = 0
            if (
                response.usage.prompt_tokens_details
                and response.usage.prompt_tokens_details.cached_tokens
            ):
                cached_tokens = response.usage.prompt_tokens_details.cached_tokens

            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens - cached_tokens,
                output_tokens=response.usage.completion_tokens,
                cached_input_tokens=cached_tokens,
                matrx_model_name=response.model,
                provider_model_name=response.model,
                api="cerebras",
                response_id=response.id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: Cerebras response missing usage data for model {response.model} (response_id: {response.id})",
                color="red",
            )

        # Map finish_reason to unified format
        finish_reason = None
        if choice.finish_reason == "stop":
            finish_reason = FinishReason.STOP
        elif choice.finish_reason == "length":
            finish_reason = FinishReason.MAX_TOKENS
        elif choice.finish_reason == "tool_calls":
            finish_reason = FinishReason.TOOL_CALLS
        elif choice.finish_reason == "content_filter":
            finish_reason = FinishReason.CONTENT_FILTER

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            stop_reason=choice.finish_reason,
            raw_response=response,
        )


# ============================================================================
# TOGETHER TRANSLATOR
# ============================================================================


class TogetherTranslator:
    """Translates between unified format and Together AI API (OpenAI-style)"""

    def to_together(self, config: UnifiedConfig) -> Dict[str, Any]:
        """
        Convert unified config to Together API format.
        
        Together uses OpenAI-style messages with full streaming + tools support.
        """
        messages = []

        # Add system message if present
        if config.system_instruction:
            messages.append({"role": "system", "content": config.system_instruction})

        # Convert messages to OpenAI-style format
        for msg in config.messages:
            if msg.role == "tool":
                # Tool results
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": content.tool_use_id or content.call_id,
                                "content": json.dumps(content.content)
                                if isinstance(content.content, (dict, list))
                                else str(content.content),
                            }
                        )
            else:
                # Regular messages
                message_dict = {"role": msg.role}
                text_parts = []
                tool_calls = []

                for content in msg.content:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif isinstance(content, ToolCallContent):
                        tool_calls.append(
                            {
                                "id": content.id,
                                "type": "function",
                                "function": {
                                    "name": content.name,
                                    "arguments": json.dumps(content.arguments),
                                },
                            }
                        )
                    elif isinstance(content, YouTubeVideoContent):
                        # YouTube URLs not supported by Together - show warning
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by Together models and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                # Set content based on what we have
                if text_parts:
                    # Has text content
                    message_dict["content"] = "".join(text_parts)
                elif tool_calls:
                    # Has tool calls but no text - set content to null for OpenAI compatibility
                    message_dict["content"] = None
                else:
                    # No text and no tool calls - set empty string
                    message_dict["content"] = ""

                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                # Append message if it has content or tool calls
                if text_parts or tool_calls or message_dict["content"] == "":
                    messages.append(message_dict)

        # Build request
        together_request = {
            "model": config.model,
            "messages": messages,
        }

        # Add optional parameters
        if config.max_output_tokens:
            together_request["max_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            together_request["temperature"] = config.temperature
        if config.top_p is not None:
            together_request["top_p"] = config.top_p
        if config.stop_sequences:
            together_request["stop"] = config.stop_sequences
        if config.response_format:
            together_request["response_format"] = config.response_format
        if config.stream:
            together_request["stream"] = True

        # Tools - Together supports streaming with tools
        if config.tools:
            together_request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(
                config.tools, "together"
            )
            if config.tool_choice:
                together_request["tool_choice"] = config.tool_choice

        vcprint(
            together_request, "--> Together Request", color="magenta", verbose=False
        )
        return together_request

    def from_together(self, response: Any) -> UnifiedResponse:
        """Convert Together API response to unified format"""
        messages = []

        if not response.choices:
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # Extract text content
        if message.content:
            content.append(TextContent(text=message.content))

        # Extract tool calls
        if message.tool_calls:
            for tc in message.tool_calls:
                arguments = (
                    json.loads(tc.function.arguments)
                    if isinstance(tc.function.arguments, str)
                    else tc.function.arguments
                )
                content.append(
                    ToolCallContent(
                        id=tc.id, name=tc.function.name, arguments=arguments
                    )
                )

        if content:
            messages.append(
                UnifiedMessage(role="assistant", content=content, id=response.id)
            )

        # Convert usage to TokenUsage
        token_usage = None
        if response.usage:
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                matrx_model_name=response.model,
                provider_model_name=response.model,
                api="together",
                response_id=response.id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: Together response missing usage data for model {response.model} (response_id: {response.id})",
                color="red",
            )

        # Map finish_reason
        finish_reason = None
        if choice.finish_reason == "stop":
            finish_reason = FinishReason.STOP
        elif choice.finish_reason == "length":
            finish_reason = FinishReason.MAX_TOKENS
        elif choice.finish_reason == "tool_calls":
            finish_reason = FinishReason.TOOL_CALLS
        elif choice.finish_reason == "content_filter":
            finish_reason = FinishReason.CONTENT_FILTER

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            stop_reason=choice.finish_reason,
            raw_response=response,
        )


# ============================================================================
# GROQ TRANSLATOR
# ============================================================================


class GroqTranslator:
    """Translates between unified format and Groq API (OpenAI-style)"""

    def to_groq(self, config: UnifiedConfig) -> Dict[str, Any]:
        """
        Convert unified config to Groq API format.
        
        Groq uses OpenAI-style messages with full streaming + tools support.
        """
        messages = []

        # Add system message if present
        if config.system_instruction:
            messages.append({"role": "system", "content": config.system_instruction})

        # Convert messages to OpenAI-style format
        for msg in config.messages:
            if msg.role == "tool":
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": content.tool_use_id or content.call_id,
                                "content": json.dumps(content.content)
                                if isinstance(content.content, (dict, list))
                                else str(content.content),
                            }
                        )
            else:
                message_dict = {"role": msg.role}
                text_parts = []
                tool_calls = []

                for content in msg.content:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif isinstance(content, ToolCallContent):
                        tool_calls.append(
                            {
                                "id": content.id,
                                "type": "function",
                                "function": {
                                    "name": content.name,
                                    "arguments": json.dumps(content.arguments),
                                },
                            }
                        )
                    elif isinstance(content, YouTubeVideoContent):
                        # YouTube URLs not supported by Groq - show warning
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by Groq models and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                # Set content based on what we have
                if text_parts:
                    # Has text content
                    message_dict["content"] = "".join(text_parts)
                elif tool_calls:
                    # Has tool calls but no text - set content to null for OpenAI compatibility
                    message_dict["content"] = None
                else:
                    # No text and no tool calls - set empty string
                    message_dict["content"] = ""

                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                # Append message if it has content or tool calls
                if text_parts or tool_calls or message_dict["content"] == "":
                    messages.append(message_dict)

        # Build request
        groq_request = {
            "model": config.model,
            "messages": messages,
        }

        # Add optional parameters
        if config.max_output_tokens:
            groq_request["max_completion_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            groq_request["temperature"] = config.temperature
        if config.top_p is not None:
            groq_request["top_p"] = config.top_p
        if config.stop_sequences:
            groq_request["stop"] = config.stop_sequences
        if config.response_format:
            groq_request["response_format"] = config.response_format
        if config.stream:
            groq_request["stream"] = True

        # Tools - Groq supports streaming with tools
        if config.tools:
            groq_request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(config.tools, "groq")
            if config.tool_choice:
                groq_request["tool_choice"] = config.tool_choice

        vcprint(groq_request, "--> Groq Request", color="magenta", verbose=False)
        return groq_request

    def from_groq(self, response: Any) -> UnifiedResponse:
        """Convert Groq API response to unified format"""
        messages = []

        if not response.choices:
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # Extract text content
        if message.content:
            content.append(TextContent(text=message.content))

        # Extract tool calls
        if message.tool_calls:
            for tc in message.tool_calls:
                arguments = (
                    json.loads(tc.function.arguments)
                    if isinstance(tc.function.arguments, str)
                    else tc.function.arguments
                )
                content.append(
                    ToolCallContent(
                        id=tc.id, name=tc.function.name, arguments=arguments
                    )
                )

        if content:
            messages.append(
                UnifiedMessage(role="assistant", content=content, id=response.id)
            )

        # Convert usage to TokenUsage
        token_usage = None
        if response.usage:
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                matrx_model_name=response.model,
                provider_model_name=response.model,
                api="groq",
                response_id=response.id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: Groq response missing usage data for model {response.model} (response_id: {response.id})",
                color="red",
            )

        # Map finish_reason
        finish_reason = None
        if choice.finish_reason == "stop":
            finish_reason = FinishReason.STOP
        elif choice.finish_reason == "length":
            finish_reason = FinishReason.MAX_TOKENS
        elif choice.finish_reason == "tool_calls":
            finish_reason = FinishReason.TOOL_CALLS
        elif choice.finish_reason == "content_filter":
            finish_reason = FinishReason.CONTENT_FILTER

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            stop_reason=choice.finish_reason,
            raw_response=response,
        )


# ============================================================================
# XAI TRANSLATOR
# ============================================================================


class XAITranslator:
    """Translates between unified format and xAI Grok API (OpenAI-compatible)"""

    def to_xai(self, config: UnifiedConfig) -> Dict[str, Any]:
        """
        Convert unified config to xAI API format.
        
        xAI uses OpenAI-compatible API with full streaming + tools support.
        """
        messages = []

        # Add system message if present
        if config.system_instruction:
            messages.append({"role": "system", "content": config.system_instruction})

        # Convert messages to OpenAI-style format
        for msg in config.messages:
            if msg.role == "tool":
                for content in msg.content:
                    if isinstance(content, ToolResultContent):
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": content.tool_use_id or content.call_id,
                                "content": json.dumps(content.content)
                                if isinstance(content.content, (dict, list))
                                else str(content.content),
                            }
                        )
            else:
                message_dict = {"role": msg.role}
                text_parts = []
                tool_calls = []

                for content in msg.content:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)
                    elif isinstance(content, ToolCallContent):
                        tool_calls.append(
                            {
                                "id": content.id,
                                "type": "function",
                                "function": {
                                    "name": content.name,
                                    "arguments": json.dumps(content.arguments),
                                },
                            }
                        )
                    elif isinstance(content, YouTubeVideoContent):
                        # YouTube URLs not supported by xAI - show warning
                        vcprint(
                            f"YouTube URL '{content.youtube_url}' is not supported by xAI models and will be skipped.",
                            "YouTube URL Warning",
                            color="yellow",
                        )

                # Set content based on what we have
                if text_parts:
                    # Has text content
                    message_dict["content"] = "".join(text_parts)
                elif tool_calls:
                    # Has tool calls but no text - set content to null for OpenAI compatibility
                    message_dict["content"] = None
                else:
                    # No text and no tool calls - set empty string
                    message_dict["content"] = ""

                if tool_calls:
                    message_dict["tool_calls"] = tool_calls

                # Append message if it has content or tool calls
                if text_parts or tool_calls or message_dict["content"] == "":
                    messages.append(message_dict)

        # Build request
        xai_request = {
            "model": config.model,
            "messages": messages,
        }

        # Add optional parameters
        if config.max_output_tokens:
            xai_request["max_completion_tokens"] = config.max_output_tokens
        if config.temperature is not None:
            xai_request["temperature"] = config.temperature
        if config.top_p is not None:
            xai_request["top_p"] = config.top_p
        if config.stop_sequences:
            xai_request["stop"] = config.stop_sequences
        if config.response_format:
            xai_request["response_format"] = config.response_format
        if config.stream:
            xai_request["stream"] = True

        # Tools - xAI supports streaming with tools
        if config.tools:
            xai_request["tools"] = ToolRegistryV2.get_instance().get_provider_tools(config.tools, "xai")
            if config.tool_choice:
                xai_request["tool_choice"] = config.tool_choice

        vcprint(xai_request, "--> xAI Request", color="magenta", verbose=False)
        return xai_request

    def from_xai(self, response: Any) -> UnifiedResponse:
        """Convert xAI API response to unified format"""
        messages = []

        if not response.choices:
            return UnifiedResponse(messages=[], finish_reason=FinishReason.ERROR)

        choice = response.choices[0]
        message = choice.message
        content = []

        # Extract text content
        if message.content:
            content.append(TextContent(text=message.content))

        # Extract tool calls
        if message.tool_calls:
            for tc in message.tool_calls:
                arguments = (
                    json.loads(tc.function.arguments)
                    if isinstance(tc.function.arguments, str)
                    else tc.function.arguments
                )
                content.append(
                    ToolCallContent(
                        id=tc.id, name=tc.function.name, arguments=arguments
                    )
                )

        if content:
            messages.append(
                UnifiedMessage(role="assistant", content=content, id=response.id)
            )

        # Convert usage to TokenUsage
        token_usage = None
        if response.usage:
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                matrx_model_name=response.model,
                provider_model_name=response.model,
                api="xai",
                response_id=response.id,
            )
        else:
            vcprint(
                f"⚠️  WARNING: xAI response missing usage data for model {response.model} (response_id: {response.id})",
                color="red",
            )

        # Map finish_reason
        finish_reason = None
        if choice.finish_reason == "stop":
            finish_reason = FinishReason.STOP
        elif choice.finish_reason == "length":
            finish_reason = FinishReason.MAX_TOKENS
        elif choice.finish_reason == "tool_calls":
            finish_reason = FinishReason.TOOL_CALLS
        elif choice.finish_reason == "content_filter":
            finish_reason = FinishReason.CONTENT_FILTER

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            stop_reason=choice.finish_reason,
            raw_response=response,
        )


# ============================================================================
# GEMINI TRANSLATOR
# ============================================================================


class GoogleProviderConfig(TypedDict):
    """Type hint for Google API configuration dictionary"""

    model: str
    contents: List[Content]
    config: GenerateContentConfig


class GoogleTranslator:
    """Translates between unified format and Google Gemini API"""

    from google.genai import types

    def to_google(self, config: UnifiedConfig, api_class: str) -> GoogleProviderConfig:
        """
        Convert unified request to Google provider format efficiently.
        Combines to_gemini and generate_google_config into a single optimized method.

        This method does everything in ONE efficient pass:
        1. Processes messages and builds 'contents' array (from to_gemini)
        2. Directly builds types.GenerateContentConfig object (from generate_google_config)
        3. Returns both in the exact structure needed by execute()

        Args:
            config: UnifiedConfig with request parameters
            api_class: API class identifier ("google_standard", "google_thinking", "google_thinking_3")

        Returns:
            Dict with:
                - contents: List of message contents in Google format
                - config: types.GenerateContentConfig object ready for API call
        """
        # ========================
        # STEP 1: Build contents (from messages)
        # ========================
        contents: List[Content] = []

        for msg in config.messages:
            google_content: Optional[Content] = msg.to_google_content()
            if google_content:
                contents.append(google_content)

        # ========================
        # STEP 2: Build GenerateContentConfig directly
        # ========================
        try:
            # Build generation config kwargs
            generation_config_kwargs = {}

            # System instruction
            if config.system_instruction:
                generation_config_kwargs["system_instruction"] = (
                    config.system_instruction
                )

            # Standard generation parameters
            if config.max_output_tokens:
                generation_config_kwargs["max_output_tokens"] = config.max_output_tokens
            if config.temperature is not None:
                generation_config_kwargs["temperature"] = config.temperature

            # API-class specific parameters
            if api_class == "google_standard":
                if config.top_p is not None:
                    generation_config_kwargs["top_p"] = config.top_p
                if config.top_k is not None:
                    generation_config_kwargs["top_k"] = config.top_k

            # # Thinking config
            # print("TO GOOGLE TRANSLATOR DEBUG")
            # print("API CLASS", api_class)
            # vcprint(config, "CONFIG", color="yellow")
            # print("--------------------------------")
            # print("--------------------------------")
            
            thinking = ThinkingConfig.from_settings(config)
            if thinking:
                if api_class == "google_thinking":
                    generation_config_kwargs["thinking_config"] = (
                        thinking.to_google_thinking_legacy()
                    )
                elif api_class == "google_thinking_3":
                    generation_config_kwargs["thinking_config"] = (
                        thinking.to_google_thinking_3()
                    )

            # Create the config object
            generated_config: GenerateContentConfig = types.GenerateContentConfig(
                **generation_config_kwargs
            )

            # ========================
            # STEP 3: Process tools directly on config object
            # ========================
            if config.tools:
                raw_tools = ToolRegistryV2.get_instance().get_provider_tools(config.tools, "google")

                # Wrap each tool in types.Tool
                generated_config.tools = [
                    types.Tool(function_declarations=[tool]) for tool in raw_tools
                ]

                # Set tool config if tool_choice is specified
                if config.tool_choice:
                    if config.tool_choice == "none":
                        mode = "NONE"
                    elif config.tool_choice == "required":
                        mode = "ANY"
                    else:
                        mode = "AUTO"

                    generated_config.tool_config = types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(mode=mode)
                    )

            else:
                # Conditionally add built-in Google tools based on config flags
                built_in_tools = []

                if config.internal_url_context:
                    built_in_tools.append(types.Tool(url_context=types.UrlContext()))

                if config.internal_web_search:
                    built_in_tools.append(types.Tool(googleSearch=types.GoogleSearch()))

                if built_in_tools:
                    generated_config.tools = built_in_tools

        except Exception as e:
            vcprint(e, "Error in to_provider_config", color="red")
            raise

        # ========================
        # STEP 4: Return final structure
        # ========================
        return {
            "model": config.model,
            "contents": contents,
            "config": generated_config,
        }

    def from_google(self, matrx_model_name: str, chunks: List[GenerateContentResponse]) -> UnifiedResponse:
        """Convert Google API response chunks to unified format"""

        content = []
        all_candidates = []
        usage_metadata = None
        finish_reason = None
        accumulated_text = ""  # Accumulator for regular text chunks
        google_thought_signature = None  # Track Google's thought_signature if present
        grounding_metadata = None
        model_version = None
        response_id = None
        last_chunk = None
        
        # Process all chunks to extract complete response
        for chunk in chunks:
            if chunk.candidates:
                for cand in chunk.candidates:
                    all_candidates.append(cand)
                    # Capture finish reason and usage metadata from final chunk
                    if cand.finish_reason:
                        finish_reason = FinishReason.from_google(cand.finish_reason)
                        usage_metadata = chunk.usage_metadata
                        model_version = chunk.model_version
                        response_id = chunk.response_id
                        last_chunk = chunk
                        
                    if cand.grounding_metadata:
                        grounding_metadata = cand.grounding_metadata

                    # Process content parts - all parts have predictable structure
                    if cand.content and cand.content.parts:
                        for part in cand.content.parts:
                            part: Part
                            
                            # vcprint(part, "PART", color="yellow")

                            # 1. Thinking content (has thought flag set)
                            if part.thought:
                                content.append(ThinkingContent.from_google(part))
                                # print(part.text)

                            # 2. Regular text (has text but no thought flag)
                            elif part.text:
                                accumulated_text += part.text
                                # Capture Google's thought_signature if present
                                if part.thought_signature:
                                    google_thought_signature = part.thought_signature

                            # 4. Tool calls and other content types
                            elif part.function_call:
                                content.append(ToolCallContent.from_google(part))
                            elif part.function_response:
                                content.append(ToolResultContent.from_google(part))
                            elif part.executable_code:
                                content.append(CodeExecutionContent.from_google(part))
                            elif part.code_execution_result:
                                content.append(
                                    CodeExecutionResultContent.from_google(part)
                                )
                            elif part.inline_data:
                                converted = (
                                    ImageContent.from_google(part)
                                    or AudioContent.from_google(part)
                                    or VideoContent.from_google(part)
                                    or DocumentContent.from_google(part)
                                )
                                if converted:
                                    content.append(converted)

                            # Handle file_data (could be YouTube URL or regular file)
                            elif part.file_data:
                                converted = (
                                    YouTubeVideoContent.from_google(part)
                                    or ImageContent.from_google(part)
                                    or AudioContent.from_google(part)
                                    or VideoContent.from_google(part)
                                    or DocumentContent.from_google(part)
                                )
                                if converted:
                                    content.append(converted)

                            # == only if no other part type is found ==
                            elif part.thought_signature:
                                content.append(ThinkingContent.from_google(part))

        # Add accumulated text as a single TextContent object if we have any
        if accumulated_text:
            metadata = {}
            if google_thought_signature:
                metadata["google_thought_signature"] = google_thought_signature
            if grounding_metadata:
                metadata["grounding_metadata"] = grounding_metadata
            content.append(
                TextContent(
                    text=accumulated_text,
                    metadata=metadata,
                )
            )

        # Build unified message from accumulated content
        messages = []
        if content:
            messages.append(
                UnifiedMessage(
                    role="assistant",
                    content=content,
                    metadata={
                        "finish_reason": finish_reason,
                    },
                )
            )

        # Convert usage_metadata to TokenUsage if present
        token_usage = None
        if usage_metadata:
            token_usage = TokenUsage.from_gemini(
                usage_metadata, matrx_model_name=matrx_model_name, provider_model_name=model_version, response_id=response_id
            )
        else:
            vcprint(
                f"⚠️  WARNING: Gemini response missing usage metadata for model {model_version}",
                color="red",
            )
            
            
        raw_response = last_chunk
        last_chunk.candidates = all_candidates

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=finish_reason,
            raw_response=raw_response,
        )
