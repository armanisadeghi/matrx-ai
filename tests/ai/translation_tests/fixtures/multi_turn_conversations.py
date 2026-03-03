"""
Comprehensive multi-turn conversation fixtures for translation round-trip testing.

Each fixture is a dict compatible with UnifiedConfig.from_dict(). Keys:
    - "model": str
    - "system_instruction": str | None
    - "messages": list[dict]  — each dict accepted by UnifiedMessage.from_dict()
    - plus any UnifiedConfig params (temperature, tools, etc.)

To add new test data:
    1. Add a new function returning a fixture dict.
    2. Append the result to ALL_FIXTURES at the bottom.
    3. Run: pytest tests/ai/translation_tests/ -v

Captured real LLM responses can also be loaded — see response_capture.py.
"""

import base64

# 1x1 red PNG (valid image, tiny payload)
TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
    "2mP8/58BAwAI/AL+hc2rNAAAAABJRU5ErkJggg=="
)

# Fake opaque signatures for each provider. Must survive round-trip intact.
FAKE_OPENAI_SIGNATURE = base64.b64decode(
    "dGhpcyBpcyBhIGZha2Ugb3BlbmFpIGVuY3J5cHRlZCBjb250ZW50IGZvciB0ZXN0aW5n"
)
FAKE_ANTHROPIC_SIGNATURE = "anthsig_fakesignaturefortesting_abcdef1234567890"
FAKE_GOOGLE_SIGNATURE = base64.b64decode(
    "dGhpcyBpcyBhIGZha2UgZ29vZ2xlIHRob3VnaHQgc2lnbmF0dXJlIGZvciB0ZXN0aW5n"
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _text(text: str, **kw) -> dict:
    return {"type": "text", "text": text, **kw}


def _thinking(*, provider: str, text: str = "", sig=None, **kw) -> dict:
    d: dict = {"type": "thinking", "text": text, "provider": provider}
    if sig is not None:
        d["signature"] = sig
    d.update(kw)
    return d


def _tool_call(name: str, arguments: dict, *, id: str = "", call_id: str = "") -> dict:
    return {"type": "tool_call", "id": id, "call_id": call_id, "name": name, "arguments": arguments}


def _tool_result(
    content, *, tool_use_id: str = "", call_id: str = "", name: str = "", is_error: bool = False
) -> dict:
    d: dict = {"type": "tool_result", "content": content, "name": name}
    if tool_use_id:
        d["tool_use_id"] = tool_use_id
    if call_id:
        d["call_id"] = call_id
    if is_error:
        d["is_error"] = True
    return d


def _image_url(url: str, mime: str = "image/jpeg") -> dict:
    return {"type": "image", "url": url, "mime_type": mime}


def _image_b64(data: str = TINY_PNG_BASE64, mime: str = "image/png") -> dict:
    return {"type": "image", "base64_data": data, "mime_type": mime}


def _image_file_uri(uri: str, mime: str = "image/jpeg") -> dict:
    return {"type": "image", "file_uri": uri, "mime_type": mime}


def _audio(url: str, mime: str = "audio/mpeg") -> dict:
    return {"type": "audio", "url": url, "mime_type": mime}


def _document(url: str, mime: str = "application/pdf") -> dict:
    return {"type": "document", "url": url, "mime_type": mime}


def _youtube(url: str) -> dict:
    return {"type": "youtube_video", "url": url}


def _code_exec(code: str, lang: str = "python") -> dict:
    return {"type": "code_execution", "code": code, "language": lang}


def _code_result(output: str, outcome: str = "success") -> dict:
    return {"type": "code_execution_result", "output": output, "outcome": outcome}


# ---------------------------------------------------------------------------
# Fixture definitions
# ---------------------------------------------------------------------------


def simple_text_conversation() -> dict:
    """3-turn text-only conversation."""
    return {
        "id": "simple_text",
        "description": "3-turn text-only",
        "model": "gpt-5",
        "system_instruction": "You are a helpful assistant.",
        "temperature": 0.7,
        "max_output_tokens": 4096,
        "messages": [
            {"role": "user", "content": [_text("What is the capital of France?")]},
            {"role": "assistant", "content": [_text("The capital of France is Paris.", id="msg_001")]},
            {"role": "user", "content": [_text("What is its population?")]},
        ],
    }


def conversation_with_openai_thinking() -> dict:
    """Multi-turn with OpenAI reasoning blocks and encrypted signatures."""
    return {
        "id": "openai_thinking",
        "description": "OpenAI reasoning + encrypted signatures, 6 messages",
        "model": "gpt-5",
        "system_instruction": "Think step by step before answering.",
        "temperature": 0.5,
        "max_output_tokens": 8192,
        "reasoning_effort": "high",
        "reasoning_summary": "detailed",
        "messages": [
            {"role": "user", "content": [_text("Find f'(x) and f''(x) for f(x)=3x^2+2x-5.")]},
            {
                "role": "output",
                "content": [
                    _thinking(
                        provider="openai",
                        id="rs_001",
                        signature=FAKE_OPENAI_SIGNATURE,
                        summary=[
                            {"type": "summary_text", "text": "Applying the power rule."},
                            {"type": "summary_text", "text": "f'(x)=6x+2, f''(x)=6."},
                        ],
                    ),
                ],
            },
            {
                "role": "assistant",
                "content": [_text("f'(x)=6x+2 and f''(x)=6.", id="msg_002")],
            },
            {"role": "user", "content": [_text("Find critical points and classify them.")]},
            {
                "role": "output",
                "content": [
                    _thinking(
                        provider="openai",
                        id="rs_002",
                        signature=FAKE_OPENAI_SIGNATURE,
                        summary=[{"type": "summary_text", "text": "x=-1/3 is a minimum."}],
                    ),
                ],
            },
            {
                "role": "assistant",
                "content": [_text("x=-1/3 is a local minimum with f(-1/3)=-16/3.", id="msg_003")],
            },
        ],
    }


def conversation_with_anthropic_thinking() -> dict:
    """Multi-turn with Anthropic thinking blocks and signatures."""
    return {
        "id": "anthropic_thinking",
        "description": "Anthropic thinking + string signature",
        "model": "claude-sonnet-4-6",
        "system_instruction": "You are a code review assistant.",
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "thinking_budget": 4096,
        "messages": [
            {
                "role": "user",
                "content": [_text("Review this:\ndef fib(n):\n  if n<=1: return n\n  return fib(n-1)+fib(n-2)")],
            },
            {
                "role": "assistant",
                "content": [
                    _thinking(
                        provider="anthropic",
                        text="O(2^n) time. Suggest memoization or iterative approach.",
                        signature=FAKE_ANTHROPIC_SIGNATURE,
                    ),
                    _text("This has O(2^n) time complexity. Use @lru_cache or iterate."),
                ],
            },
            {"role": "user", "content": [_text("Show the iterative version.")]},
            {
                "role": "assistant",
                "content": [
                    _thinking(
                        provider="anthropic",
                        text="Iterative: O(n) time, O(1) space.",
                        signature=FAKE_ANTHROPIC_SIGNATURE,
                    ),
                    _text("```python\ndef fib(n):\n  a,b=0,1\n  for _ in range(n): a,b=b,a+b\n  return a\n```"),
                ],
            },
        ],
    }


def conversation_with_google_thinking() -> dict:
    """Multi-turn with Google Gemini thought_signature (bytes)."""
    return {
        "id": "google_thinking",
        "description": "Google thinking with bytes thought_signature",
        "model": "gemini-3-pro-preview",
        "system_instruction": "You are a data scientist.",
        "temperature": 0.4,
        "max_output_tokens": 4096,
        "thinking_level": "high",
        "include_thoughts": True,
        "messages": [
            {"role": "user", "content": [_text("Explain bias-variance tradeoff.")]},
            {
                "role": "assistant",
                "content": [
                    _thinking(
                        provider="google",
                        text="Bias=underfitting, Variance=overfitting. Total=bias^2+variance+noise.",
                        signature=FAKE_GOOGLE_SIGNATURE,
                    ),
                    _text(
                        "Bias-variance tradeoff: total error = bias^2 + variance + irreducible error.",
                        metadata={"google_thought_signature": FAKE_GOOGLE_SIGNATURE},
                    ),
                ],
            },
        ],
    }


def conversation_with_tool_calls() -> dict:
    """17-message conversation with multiple tool call/result cycles."""
    return {
        "id": "tool_calls_multi_turn",
        "description": "17 messages: tool calls, results, thinking, text",
        "model": "gpt-5",
        "system_instruction": "You are a travel assistant. Use tools to help plan trips.",
        "temperature": 0.7,
        "max_output_tokens": 8192,
        "reasoning_effort": "medium",
        "messages": [
            # 1
            {"role": "user", "content": [_text("Plan my SF weekend trip.")]},
            # 2 - thinking
            {
                "role": "output",
                "content": [
                    _thinking(
                        provider="openai", id="rs_t1", signature=FAKE_OPENAI_SIGNATURE,
                        summary=[{"type": "summary_text", "text": "Check weather + activities."}],
                    ),
                ],
            },
            # 3 - assistant text
            {"role": "assistant", "content": [_text("Let me check the weather and find activities!", id="msg_t1")]},
            # 4 - tool call: weather
            {
                "role": "tool",
                "content": [_tool_call("get_weather", {"city": "San Francisco", "days": 3}, id="tool_001", call_id="call_abc")],
            },
            # 5 - tool result
            {
                "role": "tool",
                "content": [
                    _tool_result(
                        '{"forecast":[{"day":"Sat","high":65,"low":52,"cond":"Cloudy"},{"day":"Sun","high":68,"low":54,"cond":"Sunny"}]}',
                        tool_use_id="tool_001", call_id="call_abc", name="get_weather",
                    ),
                ],
            },
            # 6 - tool call: activities
            {
                "role": "tool",
                "content": [_tool_call("get_activities", {"city": "San Francisco", "category": "outdoor"}, id="tool_002", call_id="call_def")],
            },
            # 7 - activities result
            {
                "role": "tool",
                "content": [
                    _tool_result(
                        '{"activities":[{"name":"Golden Gate Walk","hours":2,"rating":4.8},{"name":"Alcatraz Tour","hours":3,"rating":4.9}]}',
                        tool_use_id="tool_002", call_id="call_def", name="get_activities",
                    ),
                ],
            },
            # 8 - thinking
            {
                "role": "output",
                "content": [
                    _thinking(
                        provider="openai", id="rs_t2", signature=FAKE_OPENAI_SIGNATURE,
                        summary=[{"type": "summary_text", "text": "Weather is great. Suggest itinerary."}],
                    ),
                ],
            },
            # 9 - assistant summary
            {"role": "assistant", "content": [_text("Weather: Sat 65°F Cloudy, Sun 68°F Sunny. Top: Golden Gate Walk, Alcatraz.", id="msg_t2")]},
            # 10 - user asks restaurants
            {"role": "user", "content": [_text("Find Italian restaurants near the wharf.")]},
            # 11 - tool call: restaurants
            {
                "role": "tool",
                "content": [_tool_call("get_restaurants", {"cuisine": "Italian", "near": "Fisherman's Wharf"}, id="tool_003", call_id="call_ghi")],
            },
            # 12 - restaurant result
            {
                "role": "tool",
                "content": [
                    _tool_result(
                        '{"restaurants":[{"name":"Scoma\'s","rating":4.6,"price":"$$$"},{"name":"Trattoria","rating":4.5,"price":"$$"}]}',
                        tool_use_id="tool_003", call_id="call_ghi", name="get_restaurants",
                    ),
                ],
            },
            # 13 - assistant restaurants
            {"role": "assistant", "content": [_text("Scoma's (4.6, $$$) and Trattoria (4.5, $$).", id="msg_t3")]},
            # 14 - user events
            {"role": "user", "content": [_text("What events are happening this weekend?")]},
            # 15 - tool call: events
            {
                "role": "tool",
                "content": [_tool_call("get_events", {"city": "San Francisco", "when": "this_weekend"}, id="tool_004", call_id="call_jkl")],
            },
            # 16 - events result
            {
                "role": "tool",
                "content": [
                    _tool_result(
                        '{"events":[{"name":"Jazz Festival","date":"Sat 7PM","price":"$35-75"},{"name":"Farmers Market","date":"Sat 8AM","price":"Free"}]}',
                        tool_use_id="tool_004", call_id="call_jkl", name="get_events",
                    ),
                ],
            },
            # 17 - final assistant
            {
                "role": "assistant",
                "content": [_text("Jazz Festival Sat 7PM ($35-75), Farmers Market Sat 8AM (Free). Enjoy!", id="msg_t5")],
            },
        ],
    }


def conversation_with_images() -> dict:
    """6-message conversation with image URL, base64, and file_uri inputs."""
    return {
        "id": "image_conversation",
        "description": "Images: URL, base64, and file_uri",
        "model": "gemini-3-pro-image-preview",
        "system_instruction": "You are a visual analysis assistant.",
        "temperature": 0.5,
        "max_output_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [
                    _text("What do you see in this image?"),
                    _image_url("https://example.com/test-image.jpg"),
                ],
            },
            {"role": "assistant", "content": [_text("A sunset over the Golden Gate Bridge.", id="msg_img1")]},
            {
                "role": "user",
                "content": [
                    _text("Compare with this:"),
                    _image_b64(TINY_PNG_BASE64, "image/png"),
                ],
            },
            {"role": "assistant", "content": [_text("The second is a minimal test image.", id="msg_img2")]},
            {
                "role": "user",
                "content": [
                    _text("And this from Cloud Storage?"),
                    _image_file_uri("gs://my-bucket/images/photo.jpg"),
                ],
            },
            {"role": "assistant", "content": [_text("A mountain landscape with a lake.", id="msg_img3")]},
        ],
    }


def conversation_with_anthropic_tool_calls() -> dict:
    """Anthropic-style: thinking + tool_use + tool_result, 8 messages."""
    return {
        "id": "anthropic_tool_calls",
        "description": "Anthropic thinking + tool_use + tool_result",
        "model": "claude-sonnet-4-6",
        "system_instruction": "You are a research assistant.",
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "thinking_budget": 4096,
        "messages": [
            {"role": "user", "content": [_text("Compare Tokyo and NYC populations.")]},
            {
                "role": "assistant",
                "content": [
                    _thinking(
                        provider="anthropic",
                        text="Need to search for population data for both cities.",
                        signature=FAKE_ANTHROPIC_SIGNATURE,
                    ),
                    _tool_call("web_search", {"query": "Tokyo population 2025"}, id="toolu_01A"),
                ],
            },
            {
                "role": "tool",
                "content": [_tool_result("Tokyo metro: ~37.4M", tool_use_id="toolu_01A", name="web_search")],
            },
            {
                "role": "assistant",
                "content": [_tool_call("web_search", {"query": "NYC population 2025"}, id="toolu_01B")],
            },
            {
                "role": "tool",
                "content": [_tool_result("NYC metro: ~20.1M", tool_use_id="toolu_01B", name="web_search")],
            },
            {
                "role": "assistant",
                "content": [_tool_call("calculator", {"expression": "37.4/20.1"}, id="toolu_01C")],
            },
            {
                "role": "tool",
                "content": [_tool_result("1.861", tool_use_id="toolu_01C", name="calculator")],
            },
            {
                "role": "assistant",
                "content": [
                    _thinking(
                        provider="anthropic",
                        text="Tokyo is ~1.86x larger than NYC in metro population.",
                        signature=FAKE_ANTHROPIC_SIGNATURE,
                    ),
                    _text("Tokyo metro (37.4M) is ~1.86x larger than NYC metro (20.1M)."),
                ],
            },
        ],
    }


def conversation_with_mixed_media() -> dict:
    """Conversation with images, documents, audio, and YouTube references."""
    return {
        "id": "mixed_media",
        "description": "Images, documents, audio, YouTube",
        "model": "gemini-3-flash-preview",
        "system_instruction": "You are a multimedia analysis assistant.",
        "temperature": 0.5,
        "max_output_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [_text("Analyze this diagram:"), _image_b64()],
            },
            {"role": "assistant", "content": [_text("Small test image. Provide the real diagram.", id="msg_mm1")]},
            {
                "role": "user",
                "content": [_text("Here's the PDF:"), _document("https://example.com/report.pdf")],
            },
            {"role": "assistant", "content": [_text("The PDF shows a microservices architecture.", id="msg_mm2")]},
            {
                "role": "user",
                "content": [_text("Tutorial video:"), _youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")],
            },
            {"role": "assistant", "content": [_text("The video covers the same architecture.", id="msg_mm3")]},
            {
                "role": "user",
                "content": [_text("My recorded questions:"), _audio("https://example.com/questions.mp3")],
            },
            {"role": "assistant", "content": [_text("You asked about scalability, deployment, and monitoring.", id="msg_mm4")]},
        ],
    }


def conversation_with_code_execution() -> dict:
    """Google-style code execution blocks."""
    return {
        "id": "code_execution",
        "description": "Code execution + results (Google feature)",
        "model": "gemini-3-pro-preview",
        "system_instruction": "You are a Python coding assistant.",
        "temperature": 0.2,
        "max_output_tokens": 4096,
        "messages": [
            {"role": "user", "content": [_text("Find the first 10 prime numbers.")]},
            {
                "role": "assistant",
                "content": [
                    _code_exec("primes=[]\nn=2\nwhile len(primes)<10:\n  if all(n%i for i in range(2,int(n**0.5)+1)): primes.append(n)\n  n+=1\nprint(primes)"),
                    _code_result("[2,3,5,7,11,13,17,19,23,29]"),
                    _text("The first 10 primes are: 2,3,5,7,11,13,17,19,23,29."),
                ],
            },
            {"role": "user", "content": [_text("Plot prime gaps up to 1000.")]},
            {
                "role": "assistant",
                "content": [
                    _code_exec("import matplotlib.pyplot as plt\n# ...sieve code...\nprint('168 primes, 167 gaps')"),
                    _code_result("168 primes, 167 gaps"),
                    _text("Generated histogram. Most common gap is 2 (twin primes)."),
                ],
            },
        ],
    }


def conversation_with_error_tool_result() -> dict:
    """Tool call returns an error."""
    return {
        "id": "error_tool_result",
        "description": "Tool call with is_error=True",
        "model": "claude-sonnet-4-6",
        "system_instruction": "You are a helpful assistant.",
        "temperature": 0.5,
        "max_output_tokens": 4096,
        "messages": [
            {"role": "user", "content": [_text("Look up user #12345.")]},
            {
                "role": "assistant",
                "content": [_tool_call("database_query", {"query": "SELECT * FROM users WHERE id=12345"}, id="toolu_err1")],
            },
            {
                "role": "tool",
                "content": [_tool_result("Error: Connection timeout", tool_use_id="toolu_err1", name="database_query", is_error=True)],
            },
            {"role": "assistant", "content": [_text("Database connection timed out. Please try again.")]},
        ],
    }


def conversation_cross_provider_thinking() -> dict:
    """Thinking from OpenAI, Anthropic, and Google in a single conversation.
    Tests that each provider's signature is isolated and preserved."""
    return {
        "id": "cross_provider_thinking",
        "description": "Mixed thinking from 3 providers in one conversation",
        "model": "gpt-5",
        "system_instruction": "Think step by step.",
        "temperature": 0.5,
        "max_output_tokens": 8192,
        "messages": [
            {"role": "user", "content": [_text("sqrt(144)?")]},
            # OpenAI thinking
            {
                "role": "output",
                "content": [
                    _thinking(provider="openai", id="rs_c1", signature=FAKE_OPENAI_SIGNATURE,
                              summary=[{"type": "summary_text", "text": "12*12=144, so sqrt=12."}]),
                ],
            },
            {"role": "assistant", "content": [_text("sqrt(144)=12.", id="msg_c1")]},
            # Anthropic thinking
            {"role": "user", "content": [_text("cbrt(27)?")]},
            {
                "role": "assistant",
                "content": [
                    _thinking(provider="anthropic", text="3^3=27, so cbrt=3.", signature=FAKE_ANTHROPIC_SIGNATURE),
                    _text("cbrt(27)=3."),
                ],
            },
            # Google thinking
            {"role": "user", "content": [_text("4th root of 256?")]},
            {
                "role": "assistant",
                "content": [
                    _thinking(provider="google", text="4^4=256, so 4th root=4.", signature=FAKE_GOOGLE_SIGNATURE),
                    _text("4th root of 256=4.", metadata={"google_thought_signature": FAKE_GOOGLE_SIGNATURE}),
                ],
            },
            {"role": "user", "content": [_text("Summarize all three.")]},
        ],
    }


def long_conversation_15_plus_turns() -> dict:
    """18-message conversation mixing text, thinking, tools, and images."""
    return {
        "id": "long_15_plus",
        "description": "18 messages: text, OpenAI thinking, tools, images",
        "model": "gpt-5",
        "system_instruction": "You are a comprehensive AI assistant.",
        "temperature": 0.5,
        "max_output_tokens": 8192,
        "reasoning_effort": "high",
        "messages": [
            # 1 image+text
            {"role": "user", "content": [_text("What style is this building?"), _image_url("https://example.com/building.jpg")]},
            # 2
            {"role": "assistant", "content": [_text("Art Deco architecture.", id="msg_l1")]},
            # 3
            {"role": "user", "content": [_text("I'm visiting Chicago. Weather today?")]},
            # 4 thinking
            {"role": "output", "content": [_thinking(provider="openai", id="rs_l1", signature=FAKE_OPENAI_SIGNATURE, summary=[{"type": "summary_text", "text": "Need Chicago weather."}])]},
            # 5 tool call
            {"role": "tool", "content": [_tool_call("get_weather", {"city": "Chicago"}, id="tool_l1", call_id="call_l1")]},
            # 6 tool result
            {"role": "tool", "content": [_tool_result('{"temp":72,"cond":"Sunny","humidity":45}', tool_use_id="tool_l1", call_id="call_l1", name="get_weather")]},
            # 7
            {"role": "assistant", "content": [_text("72°F, sunny, 45% humidity.", id="msg_l2")]},
            # 8
            {"role": "user", "content": [_text("Building is 45 stories, 3.5m each. Height in feet?")]},
            # 9 calculator
            {"role": "tool", "content": [_tool_call("calculator", {"expression": "45*3.5*3.28084"}, id="tool_l2", call_id="call_l2")]},
            # 10
            {"role": "tool", "content": [_tool_result("516.73218", tool_use_id="tool_l2", call_id="call_l2", name="calculator")]},
            # 11 thinking
            {"role": "output", "content": [_thinking(provider="openai", id="rs_l2", signature=FAKE_OPENAI_SIGNATURE, summary=[{"type": "summary_text", "text": "~516.7 feet."}])]},
            # 12
            {"role": "assistant", "content": [_text("~516.7 feet.", id="msg_l3")]},
            # 13
            {"role": "user", "content": [_text("When was Art Deco most popular in Chicago?")]},
            # 14
            {"role": "assistant", "content": [_text("Late 1920s-1930s. Chicago Board of Trade (1930).", id="msg_l4")]},
            # 15 another image
            {"role": "user", "content": [_text("Another building:"), _image_b64()]},
            # 16
            {"role": "assistant", "content": [_text("That's a test image, not a building.", id="msg_l5")]},
            # 17
            {"role": "user", "content": [_text("What other styles are famous in Chicago?")]},
            # 18
            {"role": "assistant", "content": [_text("Chicago School, Art Deco, International Style, Postmodern, Contemporary.", id="msg_l6")]},
        ],
    }


def conversation_with_parallel_tool_calls() -> dict:
    """Multiple tool calls dispatched in parallel."""
    return {
        "id": "parallel_tool_calls",
        "description": "3 parallel tool calls + results",
        "model": "gpt-5",
        "system_instruction": "Use tools efficiently.",
        "temperature": 0.5,
        "max_output_tokens": 4096,
        "messages": [
            {"role": "user", "content": [_text("Weather, location, and events nearby?")]},
            {"role": "tool", "content": [_tool_call("get_weather", {"city": "auto"}, id="tp1", call_id="cp1")]},
            {"role": "tool", "content": [_tool_call("get_location", {}, id="tp2", call_id="cp2")]},
            {"role": "tool", "content": [_tool_call("get_events", {"nearby": True}, id="tp3", call_id="cp3")]},
            {"role": "tool", "content": [_tool_result('{"temp":75,"cond":"Sunny"}', tool_use_id="tp1", call_id="cp1", name="get_weather")]},
            {"role": "tool", "content": [_tool_result('{"city":"Austin","state":"TX"}', tool_use_id="tp2", call_id="cp2", name="get_location")]},
            {"role": "tool", "content": [_tool_result('{"events":[{"name":"SXSW","time":"6PM"}]}', tool_use_id="tp3", call_id="cp3", name="get_events")]},
            {"role": "assistant", "content": [_text("Austin TX, 75°F Sunny, SXSW at 6PM.", id="msg_p1")]},
        ],
    }


def conversation_with_complex_tool_arguments() -> dict:
    """Deeply nested tool call arguments and list results."""
    return {
        "id": "complex_tool_args",
        "description": "Complex nested JSON arguments",
        "model": "claude-sonnet-4-6",
        "system_instruction": "You are a data analyst.",
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "messages": [
            {"role": "user", "content": [_text("Top 5 products by revenue bar chart.")]},
            {
                "role": "assistant",
                "content": [
                    _tool_call(
                        "database_query",
                        {
                            "query": "SELECT product_name, SUM(revenue) AS rev FROM sales GROUP BY product_name ORDER BY rev DESC LIMIT 5",
                            "params": {"timeout": 30, "cache": True},
                            "output_format": {"type": "json", "include_metadata": True},
                        },
                        id="toolu_cta1",
                    ),
                ],
            },
            {
                "role": "tool",
                "content": [
                    _tool_result(
                        [
                            {"product_name": "Widget Pro", "total_revenue": 1250000},
                            {"product_name": "Super Gadget", "total_revenue": 980000},
                            {"product_name": "MegaTool", "total_revenue": 750000},
                        ],
                        tool_use_id="toolu_cta1",
                        name="database_query",
                    ),
                ],
            },
            {
                "role": "assistant",
                "content": [
                    _tool_call(
                        "create_chart",
                        {
                            "chart_type": "bar",
                            "title": "Top 5 Products",
                            "data": {
                                "labels": ["Widget Pro", "Super Gadget", "MegaTool"],
                                "values": [1250000, 980000, 750000],
                            },
                            "options": {
                                "colors": ["#4CAF50", "#2196F3", "#FF9800"],
                                "y_axis": {"label": "Revenue ($)", "format": "currency"},
                                "annotations": [{"label": "Target", "value": 1000000, "style": "dashed"}],
                            },
                        },
                        id="toolu_cta2",
                    ),
                ],
            },
            {
                "role": "tool",
                "content": [
                    _tool_result(
                        '{"chart_url":"https://charts.matrx.app/abc123","format":"png","dim":{"w":800,"h":600}}',
                        tool_use_id="toolu_cta2",
                        name="create_chart",
                    ),
                ],
            },
            {"role": "assistant", "content": [_text("Widget Pro leads with $1.25M.")]},
        ],
    }


# ============================================================================
# REGISTRY
# ============================================================================

ALL_FIXTURES: list[dict] = [
    simple_text_conversation(),
    conversation_with_openai_thinking(),
    conversation_with_anthropic_thinking(),
    conversation_with_google_thinking(),
    conversation_with_tool_calls(),
    conversation_with_images(),
    conversation_with_anthropic_tool_calls(),
    conversation_with_mixed_media(),
    conversation_with_code_execution(),
    conversation_with_error_tool_result(),
    conversation_cross_provider_thinking(),
    long_conversation_15_plus_turns(),
    conversation_with_parallel_tool_calls(),
    conversation_with_complex_tool_arguments(),
]


def get_fixture_by_id(fixture_id: str) -> dict | None:
    for f in ALL_FIXTURES:
        if f["id"] == fixture_id:
            return f
    return None


def get_all_fixture_ids() -> list[str]:
    return [f["id"] for f in ALL_FIXTURES]
