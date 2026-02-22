from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class TimingUsage:
    """Tracks timing information for a single request iteration."""

    start_time: float
    end_time: Optional[float] = None

    # Component timings
    api_call_duration: float = 0.0
    tool_execution_duration: float = 0.0

    # Context
    model: str = ""
    iteration: int = 0

    @property
    def total_duration(self) -> float:
        """Total duration of this iteration in seconds."""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def processing_duration(self) -> float:
        """Time spent processing logic outside of API and Tools."""
        return max(
            0.0,
            self.total_duration - self.api_call_duration - self.tool_execution_duration,
        )

    @staticmethod
    def aggregate(timings: List["TimingUsage"]) -> Dict[str, Any]:
        """Aggregate timing statistics from a list of iteration timings.

        Returns a dictionary with comprehensive timing analysis including:
        - Total wall-clock duration
        - Total time spent in API calls
        - Total time spent executing tools
        - Average times for each component
        """
        if not timings:
            return {
                "total_duration": 0.0,
                "api_duration": 0.0,
                "tool_duration": 0.0,
                "processing_duration": 0.0,
            }

        valid_timings = [t for t in timings if t.end_time is not None]
        if not valid_timings:
            return {
                "total_duration": 0.0,
                "api_duration": 0.0,
                "tool_duration": 0.0,
                "processing_duration": 0.0,
            }

        # Calculate totals
        total_api = sum(t.api_call_duration for t in valid_timings)
        total_tool = sum(t.tool_execution_duration for t in valid_timings)
        total_sum_duration = sum(t.total_duration for t in valid_timings)

        # Calculate wall clock duration (from start of first to end of last)
        # Sort just in case they aren't in order (though they should be)
        sorted_timings = sorted(valid_timings, key=lambda t: t.start_time)
        wall_clock_start = sorted_timings[0].start_time
        wall_clock_end = sorted_timings[-1].end_time
        wall_clock_duration = wall_clock_end - wall_clock_start

        return {
            "total_duration": wall_clock_duration,
            "sum_duration": total_sum_duration,
            "api_duration": total_api,
            "tool_duration": total_tool,
            "processing_duration": max(
                0.0, wall_clock_duration - total_api - total_tool
            ),
            "iterations": len(valid_timings),
            "avg_iteration_duration": wall_clock_duration / len(valid_timings)
            if valid_timings
            else 0,
        }
