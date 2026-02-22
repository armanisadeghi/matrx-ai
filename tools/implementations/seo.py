from __future__ import annotations

import traceback
from datetime import datetime
from typing import Any

from tools.models import ToolContext, ToolError, ToolResult


async def check_meta_titles(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from seo.utils.meta_calculators import calculate_meta_title_metrics

    titles = args.get("titles", [])
    if isinstance(titles, str):
        titles = [titles]
    if not titles:
        return ToolResult(success=False, error=ToolError(error_type="validation", message="titles must be a non-empty string or list of strings."))

    try:
        analysis = []
        for title in titles:
            metrics = calculate_meta_title_metrics(title)
            title_ok = metrics.get("desktop_ok", False) and metrics.get("mobile_ok", False) and metrics.get("seo_length_ok", False)
            analysis.append({
                "title": title,
                "pixel_width": metrics.get("pixel_width"),
                "character_count": metrics.get("character_count"),
                "desktop_ok": metrics.get("desktop_ok"),
                "mobile_ok": metrics.get("mobile_ok"),
                "seo_length_ok": metrics.get("seo_length_ok"),
                "title_ok": title_ok,
            })
        return ToolResult(success=True, output={"title_analysis": analysis, "count": len(analysis)})
    except Exception as e:
        return ToolResult(success=False, error=ToolError(error_type="execution", message=str(e), traceback=traceback.format_exc()))


async def check_meta_descriptions(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from seo.utils.meta_calculators import calculate_meta_description_metrics

    descriptions = args.get("descriptions", [])
    if isinstance(descriptions, str):
        descriptions = [descriptions]
    if not descriptions:
        return ToolResult(success=False, error=ToolError(error_type="validation", message="descriptions must be a non-empty string or list of strings."))

    try:
        analysis = []
        for desc in descriptions:
            metrics = calculate_meta_description_metrics(desc)
            desc_ok = metrics.get("desktop_ok", False) and metrics.get("seo_length_ok", False)
            analysis.append({
                "description": desc,
                "pixel_width": metrics.get("pixel_width"),
                "character_count": metrics.get("character_count"),
                "desktop_ok": metrics.get("desktop_ok"),
                "seo_length_ok": metrics.get("seo_length_ok"),
                "description_ok": desc_ok,
            })
        return ToolResult(success=True, output={"description_analysis": analysis, "count": len(analysis)})
    except Exception as e:
        return ToolResult(success=False, error=ToolError(error_type="execution", message=str(e), traceback=traceback.format_exc()))


async def check_meta_tags_batch(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from seo.utils.meta_calculators import analyze_meta_tags_batch

    meta_data = args.get("meta_data", [])
    if not meta_data or not isinstance(meta_data, list):
        return ToolResult(success=False, error=ToolError(error_type="validation", message="meta_data must be a non-empty list of objects with 'title' and/or 'description'."))

    for idx, item in enumerate(meta_data):
        if not isinstance(item, dict) or ("title" not in item and "description" not in item):
            return ToolResult(
                success=False,
                error=ToolError(error_type="validation", message=f"Item at index {idx} must have at least 'title' or 'description'."),
            )

    try:
        result = analyze_meta_tags_batch(meta_data)
        return ToolResult(success=True, output={"batch_analysis": result, "count": len(meta_data)})
    except Exception as e:
        return ToolResult(success=False, error=ToolError(error_type="execution", message=str(e), traceback=traceback.format_exc()))


async def get_keyword_search_data(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from api_management.api_sdks.data_for_seo.data_for_seo import keyword_research
    import json

    keywords = args.get("keywords", [])
    date_from = args.get("date_from", "")
    date_to = args.get("date_to", "")
    location_code = args.get("location_code", 2840)
    language_code = args.get("language_code", "en")
    search_partners = args.get("search_partners", True)
    sort_by = args.get("sort_by", "search_volume")

    if not keywords or not isinstance(keywords, list):
        return ToolResult(success=False, error=ToolError(error_type="validation", message="keywords must be a non-empty list of strings."))
    if not date_from or not date_to:
        return ToolResult(success=False, error=ToolError(error_type="validation", message="date_from and date_to are required (YYYY-MM-DD)."))

    try:
        datetime.strptime(date_from, "%Y-%m-%d")
        datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        return ToolResult(success=False, error=ToolError(error_type="validation", message="date_from and date_to must be valid dates in YYYY-MM-DD format."))

    try:
        response = keyword_research(
            keywords=keywords,
            date_from=date_from,
            date_to=date_to,
            location_code=location_code,
            language_code=language_code,
            search_partners=search_partners,
            sort_by=sort_by,
        )
        data = json.loads(response) if isinstance(response, str) else response

        tasks = data.get("tasks", [])
        if not tasks or tasks[0].get("status_code") != 20000:
            return ToolResult(success=False, error=ToolError(error_type="api_error", message=f"DataForSEO API error: {tasks[0].get('status_message', 'Unknown') if tasks else 'No tasks returned'}"))

        result_data = tasks[0].get("result", [])
        return ToolResult(success=True, output={
            "keywords_data": result_data,
            "total_keywords": len(keywords),
            "date_range": {"from": date_from, "to": date_to},
            "search_parameters": {"location_code": location_code, "language_code": language_code},
        })
    except Exception as e:
        return ToolResult(success=False, error=ToolError(error_type="execution", message=str(e), traceback=traceback.format_exc()))
