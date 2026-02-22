from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ToolCallUsage:
    """Tracks tool call information for a single request iteration."""

    iteration: int
    tool_calls_count: int
    """Number of tool calls made in this iteration"""

    tool_calls_details: List[Dict[str, Any]]
    """List of tool call details (name, success, etc.)"""

    @staticmethod
    def aggregate(tool_call_list: List["ToolCallUsage"]) -> Dict[str, Any]:
        """Aggregate tool call statistics from a list of iteration tool calls.

        Returns a dictionary with comprehensive tool call analysis including:
        - Total tool calls across all iterations
        - Breakdown by tool name
        - Success/failure counts
        """
        if not tool_call_list:
            return {
                "total_tool_calls": 0,
                "iterations_with_tools": 0,
                "by_tool": {},
            }

        total_calls = sum(tc.tool_calls_count for tc in tool_call_list)
        iterations_with_tools = len([tc for tc in tool_call_list if tc.tool_calls_count > 0])

        # Aggregate by tool name
        by_tool: Dict[str, Dict[str, int]] = {}

        for tc in tool_call_list:
            for detail in tc.tool_calls_details:
                tool_name = detail.get("name", "unknown")
                if tool_name not in by_tool:
                    by_tool[tool_name] = {
                        "count": 0,
                        "success": 0,
                        "error": 0,
                    }

                by_tool[tool_name]["count"] += 1
                
                # Track success/error if available
                if detail.get("success", True):  # Default to True if not specified
                    by_tool[tool_name]["success"] += 1
                else:
                    by_tool[tool_name]["error"] += 1

        return {
            "total_tool_calls": total_calls,
            "iterations_with_tools": iterations_with_tools,
            "by_tool": by_tool,
        }

