"""
Monitoring for MCP Server Tool Usage
Provides metrics and monitoring for MCP tool usage
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
import threading
import json


class MCPTaskUsageMonitor:
    """
    Monitors MCP tool usage for analytics and performance tracking.
    Tracks metrics like requests per tool, response times, success rates, etc.
    """

    def __init__(self):
        self.tool_call_counts: Dict[str, int] = defaultdict(int)
        self.tool_success_counts: Dict[str, int] = defaultdict(int)
        self.tool_error_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.recent_calls = deque(maxlen=1000)  # Keep last 1000 calls for analysis
        self.lock = threading.Lock()

    def record_tool_call(self, tool_name: str, user_id: str, success: bool, response_time: float):
        """
        Record a tool call for monitoring purposes.

        Args:
            tool_name: The name of the tool that was called
            user_id: The ID of the user who made the call
            success: Whether the call was successful
            response_time: The time it took to process the call in seconds
        """
        with self.lock:
            # Update counters
            self.tool_call_counts[tool_name] += 1

            if success:
                self.tool_success_counts[tool_name] += 1
            else:
                self.tool_error_counts[tool_name] += 1

            # Track response time
            self.response_times[tool_name].append(response_time)

            # Add to recent calls for analysis
            call_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "tool_name": tool_name,
                "user_id": user_id,
                "success": success,
                "response_time": response_time
            }
            self.recent_calls.append(call_record)

    def get_tool_stats(self, tool_name: str) -> Dict:
        """
        Get statistics for a specific tool.

        Args:
            tool_name: The name of the tool to get stats for

        Returns:
            Dictionary containing statistics for the tool
        """
        with self.lock:
            total_calls = self.tool_call_counts[tool_name]
            successful_calls = self.tool_success_counts[tool_name]
            error_calls = self.tool_error_counts[tool_name]

            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

            response_times = self.response_times[tool_name]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0

            return {
                "tool_name": tool_name,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "error_calls": error_calls,
                "success_rate_percent": round(success_rate, 2),
                "average_response_time_seconds": round(avg_response_time, 4),
                "max_response_time_seconds": round(max_response_time, 4),
                "min_response_time_seconds": round(min_response_time, 4),
                "response_time_samples": len(response_times)
            }

    def get_all_tool_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all tools.

        Returns:
            Dictionary mapping tool names to their statistics
        """
        with self.lock:
            stats = {}
            for tool_name in self.tool_call_counts.keys():
                stats[tool_name] = self.get_tool_stats(tool_name)
            return stats

    def get_system_health(self) -> Dict:
        """
        Get overall system health metrics.

        Returns:
            Dictionary containing system health metrics
        """
        with self.lock:
            total_calls = sum(self.tool_call_counts.values())
            total_successful = sum(self.tool_success_counts.values())
            total_errors = sum(self.tool_error_counts.values())

            success_rate = (total_successful / total_calls * 100) if total_calls > 0 else 0

            # Calculate average response time across all tools
            all_response_times = []
            for times in self.response_times.values():
                all_response_times.extend(times)

            avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0

            return {
                "total_calls": total_calls,
                "total_successful": total_successful,
                "total_errors": total_errors,
                "overall_success_rate_percent": round(success_rate, 2),
                "average_response_time_seconds": round(avg_response_time, 4),
                "monitored_tools_count": len(set(self.tool_call_counts.keys())),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_recent_activity(self, limit: int = 50) -> List[Dict]:
        """
        Get recent tool call activity.

        Args:
            limit: Maximum number of recent calls to return

        Returns:
            List of recent tool call records
        """
        with self.lock:
            recent_list = list(self.recent_calls)
            return recent_list[-limit:] if len(recent_list) >= limit else recent_list

    def reset_stats(self):
        """
        Reset all monitoring statistics.
        """
        with self.lock:
            self.tool_call_counts.clear()
            self.tool_success_counts.clear()
            self.tool_error_counts.clear()
            self.response_times.clear()
            self.recent_calls.clear()


# Global monitor instance
mcp_monitor = MCPTaskUsageMonitor()


def record_tool_call(tool_name: str, user_id: str, success: bool, response_time: float):
    """
    Record a tool call for monitoring purposes.

    Args:
        tool_name: The name of the tool that was called
        user_id: The ID of the user who made the call
        success: Whether the call was successful
        response_time: The time it took to process the call in seconds
    """
    mcp_monitor.record_tool_call(tool_name, user_id, success, response_time)


def get_tool_stats(tool_name: str) -> Dict:
    """
    Get statistics for a specific tool.

    Args:
        tool_name: The name of the tool to get stats for

    Returns:
        Dictionary containing statistics for the tool
    """
    return mcp_monitor.get_tool_stats(tool_name)


def get_all_tool_stats() -> Dict[str, Dict]:
    """
    Get statistics for all tools.

    Returns:
        Dictionary mapping tool names to their statistics
    """
    return mcp_monitor.get_all_tool_stats()


def get_system_health() -> Dict:
    """
    Get overall system health metrics.

    Returns:
        Dictionary containing system health metrics
    """
    return mcp_monitor.get_system_health()


def get_recent_activity(limit: int = 50) -> List[Dict]:
    """
    Get recent tool call activity.

    Args:
        limit: Maximum number of recent calls to return

    Returns:
        List of recent tool call records
    """
    return mcp_monitor.get_recent_activity(limit)


def reset_monitoring_stats():
    """
    Reset all monitoring statistics.
    """
    mcp_monitor.reset_stats()