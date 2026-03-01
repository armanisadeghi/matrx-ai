from __future__ import annotations

import re
import time
from collections import Counter
from typing import Any

from tools.arg_models.text_args import RegexExtractArgs, TextAnalyzeArgs
from tools.models import ToolContext, ToolError, ToolResult


async def text_analyze(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = TextAnalyzeArgs(**args)
    text = parsed.text

    analysis_type = parsed.analysis_type.lower()
    output: dict[str, Any] = {"analysis_type": analysis_type}

    if analysis_type == "summary":
        words = text.split()
        output["word_count"] = len(words)
        output["char_count"] = len(text)
        output["sentence_count"] = len(re.split(r"[.!?]+", text.strip()))
        output["paragraph_count"] = len([p for p in text.split("\n\n") if p.strip()])

    elif analysis_type == "keywords":
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        stop_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "her",
            "was",
            "one",
            "our",
            "out",
            "has",
            "have",
            "with",
            "this",
            "that",
            "from",
            "they",
            "been",
            "said",
            "each",
            "which",
            "their",
            "will",
            "other",
            "about",
        }
        filtered = [w for w in words if w not in stop_words]
        counter = Counter(filtered)
        output["keywords"] = [
            {"word": w, "count": c} for w, c in counter.most_common(20)
        ]

    elif analysis_type == "entities":
        patterns = {
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "urls": r"https?://[^\s<>\"]+",
            "phones": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "dates": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        }
        for entity_type, pattern in patterns.items():
            output[entity_type] = list(set(re.findall(pattern, text)))

    elif analysis_type == "language":
        output["char_count"] = len(text)
        output["word_count"] = len(text.split())
        output["unique_words"] = len(set(text.lower().split()))
        output["avg_word_length"] = round(
            sum(len(w) for w in text.split()) / max(len(text.split()), 1), 1
        )
    else:
        output["message"] = (
            f"Unknown analysis type '{analysis_type}'. Supported: summary, keywords, entities, language."
        )

    return ToolResult(
        success=True,
        output=output,
        started_at=started_at,
        completed_at=time.time(),
        tool_name="text_analyze",
        call_id=ctx.call_id,
    )


async def text_regex_extract(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = RegexExtractArgs(**args)

    try:
        if parsed.find_all:
            matches = re.findall(parsed.pattern, parsed.text)
            return ToolResult(
                success=True,
                output={"matches": matches, "count": len(matches)},
                started_at=started_at,
                completed_at=time.time(),
                tool_name="regex_extract",
                call_id=ctx.call_id,
            )
        else:
            match = re.search(parsed.pattern, parsed.text)
            if match:
                return ToolResult(
                    success=True,
                    output={
                        "match": match.group(parsed.group),
                        "span": list(match.span()),
                    },
                    started_at=started_at,
                    completed_at=time.time(),
                    tool_name="regex_extract",
                    call_id=ctx.call_id,
                )
            return ToolResult(
                success=True,
                output={"match": None, "message": "No match found"},
                started_at=started_at,
                completed_at=time.time(),
                tool_name="regex_extract",
                call_id=ctx.call_id,
            )
    except re.error as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="regex",
                message=f"Invalid regex pattern: {exc}",
                suggested_action="Check the regex syntax and try again.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="regex_extract",
            call_id=ctx.call_id,
        )
