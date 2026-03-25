from __future__ import annotations

import asyncio
import json
import os
import traceback
from typing import Any

from matrx_utils import vcprint
from openai import AsyncOpenAI

from matrx_ai.config import (
    FinishReason,
    TextContent,
    TokenUsage,
    ToolCallContent,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
)
from matrx_ai.context.emitter_protocol import Emitter

from .translator import GenericOpenAITranslator

DEBUG_OVERRIDE = False


class GenericOpenAIChat:
    """
    Generic OpenAI-compatible endpoint implementation.

    Works with any provider that exposes an OpenAI-compatible chat completions API:
    - HuggingFace Inference Endpoints (TGI, llama.cpp)
    - vLLM
    - LocalAI
    - Ollama
    - Any other OpenAI-compatible server

    Usage:
        client = GenericOpenAIChat(
            base_url="https://your-endpoint.huggingface.cloud",
            api_key_env="HUGGING_FACE_TOKEN_ID",
            provider_name="huggingface",
        )
    """

    client: AsyncOpenAI
    endpoint_name: str
    provider_name: str
    debug: bool

    def __init__(
        self,
        base_url: str,
        api_key_env: str = "HUGGING_FACE_TOKEN_ID",
        provider_name: str = "generic_openai",
        api_key: str | None = None,
        debug: bool = False,
    ):
        resolved_key = api_key or os.environ.get(api_key_env, "")
        # HuggingFace TGI / llama.cpp expects the Bearer token as the API key
        self.client = AsyncOpenAI(
            api_key=resolved_key,
            base_url=base_url.rstrip("/") + "/v1",
        )
        self.provider_name = provider_name
        self.endpoint_name = f"[{provider_name.upper()} CHAT]"
        self.translator = GenericOpenAITranslator(debug=debug)
        self.debug = debug

        if DEBUG_OVERRIDE:
            self.debug = True

    def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]:
        return self.translator.to_generic_openai(config, self.provider_name)

    def to_unified_response(self, response: Any, model: str = "") -> UnifiedResponse:
        return self.translator.from_generic_openai(response, self.provider_name)

    async def execute(
        self,
        unified_config: UnifiedConfig,
        api_class: str,
        debug: bool = False,
    ) -> UnifiedResponse:
        from matrx_ai.context.app_context import get_app_context

        emitter = get_app_context().emitter
        self.debug = debug
        if DEBUG_OVERRIDE:
            self.debug = True
        self.translator.debug = debug

        config_data = self.to_provider_config(unified_config, api_class)

        vcprint(config_data, f"{self.endpoint_name} Config Data", color="blue", verbose=debug)

        try:
            if config_data.get("stream", False):
                return await self._execute_streaming(config_data, emitter, unified_config.model)
            else:
                return await self._execute_non_streaming(config_data, emitter, unified_config.model)

        except Exception as e:
            from matrx_ai.providers.errors import classify_provider_error

            error_info = classify_provider_error(self.provider_name, e)

            await emitter.send_error(
                error_type=error_info.error_type,
                message=error_info.message,
                user_message=error_info.user_message,
            )
            vcprint(e, f"{self.endpoint_name} Error", color="red")
            traceback.print_exc()

            e.error_info = error_info
            raise

    async def _execute_non_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        model: str,
    ) -> UnifiedResponse:
        vcprint(f"{self.endpoint_name} Starting API call (non-streaming)...", color="cyan")

        response = await self.client.chat.completions.create(**config_data)

        vcprint(f"{self.endpoint_name} API call completed, processing response...", color="cyan")
        vcprint(response, f"{self.endpoint_name} Response", color="green", verbose=self.debug)

        converted_response = self.to_unified_response(response, model)
        vcprint(
            f"{self.endpoint_name} Conversion complete. {len(converted_response.messages)} messages",
            color="cyan",
        )

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

        vcprint(f"{self.endpoint_name} Non-streaming execution completed successfully", color="green")
        return converted_response

    async def _execute_streaming(
        self,
        config_data: dict[str, Any],
        emitter: Emitter,
        model: str,
    ) -> UnifiedResponse:
        vcprint(f"{self.endpoint_name} Starting API call (streaming)...", color="cyan")

        stream = await self.client.chat.completions.create(**config_data)

        vcprint(f"{self.endpoint_name} Stream connection established, processing chunks...", color="cyan")

        accumulated_content = ""
        accumulated_reasoning = ""
        accumulated_tool_calls: list[dict[str, str]] = []
        usage_data = None
        finish_reason = None
        response_id = None
        in_think_block = False

        async for chunk in stream:
            response_id = chunk.id

            if chunk.usage:
                usage_data = chunk.usage

            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            # llama.cpp / Qwen3-thinking streams reasoning in delta.reasoning_content
            reasoning_chunk = getattr(delta, "reasoning_content", None)
            if reasoning_chunk:
                accumulated_reasoning += reasoning_chunk
                if not in_think_block:
                    await emitter.send_chunk("<reasoning>")
                    in_think_block = True
                await emitter.send_chunk(reasoning_chunk)
                await asyncio.sleep(0)

            if delta.content:
                # Close reasoning block before first real content token
                if in_think_block:
                    await emitter.send_chunk("\n</reasoning>\n")
                    in_think_block = False
                accumulated_content += delta.content
                await emitter.send_chunk(delta.content)
                await asyncio.sleep(0)

            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tc in delta.tool_calls:
                    tc_index_raw = (
                        tc.get("index") if isinstance(tc, dict) else getattr(tc, "index", None)
                    )
                    tc_index = int(tc_index_raw) if tc_index_raw is not None else None
                    if tc_index is None:
                        continue

                    tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                    tc_func = (
                        tc.get("function") if isinstance(tc, dict) else getattr(tc, "function", None)
                    )

                    while len(accumulated_tool_calls) <= tc_index:
                        accumulated_tool_calls.append({"id": "", "name": "", "arguments": ""})

                    if tc_id:
                        accumulated_tool_calls[tc_index]["id"] = tc_id

                    if tc_func:
                        func_name = (
                            tc_func.get("name") if isinstance(tc_func, dict) else getattr(tc_func, "name", None)
                        )
                        func_args = (
                            tc_func.get("arguments") if isinstance(tc_func, dict) else getattr(tc_func, "arguments", None)
                        )
                        if func_name:
                            accumulated_tool_calls[tc_index]["name"] = func_name
                        if func_args:
                            if isinstance(func_args, dict):
                                accumulated_tool_calls[tc_index]["arguments"] = json.dumps(func_args)
                            else:
                                accumulated_tool_calls[tc_index]["arguments"] += func_args

            if choice.finish_reason:
                finish_reason = choice.finish_reason

        # Close unclosed reasoning block (e.g. hit max_tokens mid-reasoning)
        if in_think_block:
            await emitter.send_chunk("\n</reasoning>")

        content = []

        if accumulated_content:
            content.append(TextContent(text=accumulated_content))
        elif accumulated_reasoning:
            # Hit token limit before producing a final answer — surface the reasoning
            content.append(TextContent(text=f"<think>{accumulated_reasoning}</think>"))

        for tc_data in accumulated_tool_calls:
            if tc_data["name"]:
                arguments = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                content.append(
                    ToolCallContent(id=tc_data["id"], name=tc_data["name"], arguments=arguments)
                )

        messages = []
        if content:
            messages.append(UnifiedMessage(role="assistant", content=content, id=response_id))

        token_usage = None
        if usage_data:
            token_usage = TokenUsage(
                input_tokens=usage_data.prompt_tokens,
                output_tokens=usage_data.completion_tokens,
                matrx_model_name=model,
                provider_model_name=model,
                api=self.provider_name,
                response_id=response_id or "",
            )

        unified_finish_reason = None
        if finish_reason == "stop":
            unified_finish_reason = FinishReason.STOP
        elif finish_reason == "length":
            unified_finish_reason = FinishReason.MAX_TOKENS
        elif finish_reason == "tool_calls":
            unified_finish_reason = FinishReason.TOOL_CALLS
        elif finish_reason == "content_filter":
            unified_finish_reason = FinishReason.CONTENT_FILTER

        vcprint(f"{self.endpoint_name} Streaming execution completed successfully", color="green")

        return UnifiedResponse(
            messages=messages,
            usage=token_usage,
            finish_reason=unified_finish_reason,
            stop_reason=finish_reason,
        )
