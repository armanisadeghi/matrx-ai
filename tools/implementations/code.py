from __future__ import annotations

import os
import traceback
from typing import Any

import requests

from tools.models import ToolContext, ToolError, ToolResult


async def store_html(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    html_input = args.get("html_input", "")
    if not html_input:
        return ToolResult(success=False, error=ToolError(error_type="validation", message="html_input is required."))

    api_url = "http://d88ooscwwggkcwswg8gks4s8.matrxserver.com:3000/store-html"
    try:
        response = requests.post(api_url, json={"html": html_input}, timeout=15)
        response.raise_for_status()
        return ToolResult(success=True, output={"id": response.json().get("id")})
    except requests.RequestException as e:
        return ToolResult(success=False, error=ToolError(error_type="execution", message=f"Failed to store HTML: {e}"))


async def fetch_code(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    from code_generator.code_fetcher.fetcher import get_directory_and_file_lists, prepare_data

    project_root = args.get("project_root", "")
    directory_to_fetch = args.get("directory_to_fetch", "")
    output_type = args.get("output_type", "clean_code")

    if not project_root or not os.path.isdir(project_root):
        return ToolResult(success=False, error=ToolError(error_type="validation", message=f"Project root '{project_root}' is not a valid directory."))

    full_path = os.path.join(project_root, directory_to_fetch)
    if not os.path.isdir(full_path):
        return ToolResult(success=False, error=ToolError(error_type="validation", message=f"Directory '{full_path}' does not exist."))

    valid_types = ["all_code", "clean_code", "classes_and_functions", "directory_structure"]
    if output_type not in valid_types:
        return ToolResult(success=False, error=ToolError(error_type="validation", message=f"output_type must be one of {valid_types}."))

    try:
        _, _, _, included_files = get_directory_and_file_lists(project_root=project_root, directory_to_fetch=directory_to_fetch)
        all_code_data, clean_code_data, cls_and_func_data, _ = prepare_data(included_files)

        type_map = {
            "all_code": (all_code_data, "Full code including comments and directory structure."),
            "clean_code": (clean_code_data, "Code without comments/docstrings."),
            "classes_and_functions": (cls_and_func_data, "Class and function names with arguments."),
            "directory_structure": ({"Directory Structure": all_code_data.get("Directory Structure", "")}, "Directory structure only."),
        }

        data, description = type_map[output_type]

        output_text = f"Project Root: {project_root}\nDirectory: {directory_to_fetch}\nType: {output_type} ({description})\n\n"
        for file_path, content in data.items():
            if file_path == "Directory Structure":
                output_text += f'**DIRECTORY STRUCTURE: "{project_root}"**\n\n{content}\n'
            else:
                relative = os.path.normpath(os.path.relpath(file_path, start=project_root)).replace("\\", "/")
                output_text += f"\n**Module: {relative}**\n\n"
                if isinstance(content, dict):
                    for key, value in content.items():
                        output_text += f"{key}: {value}\n"
                else:
                    output_text += f"{content}\n"

        return ToolResult(success=True, output=output_text)
    except Exception as e:
        return ToolResult(success=False, error=ToolError(error_type="execution", message=str(e), traceback=traceback.format_exc()))
