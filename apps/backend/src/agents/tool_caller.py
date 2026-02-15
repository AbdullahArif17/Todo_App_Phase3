"""
Tool Caller for Todo Agent
Handles the execution of MCP tools called by the OpenAI agent
"""
from typing import Dict, Any, List
import json
import uuid
from sqlmodel import Session

from ..mcp_server.main import mcp_todo_server


class MCPTodoToolCaller:
    """
    Handles execution of MCP tools for the Todo Agent.
    Connects to the MCP server to execute tools when requested by the agent.
    """

    def __init__(self):
        # In a real implementation, we would connect to the MCP server
        # For now, we'll use the server instance directly
        self.server = mcp_todo_server.get_server()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Call an MCP tool with the given arguments.

        Args:
            tool_name: Name of the tool to call (e.g., 'add_task', 'list_tasks')
            arguments: Arguments to pass to the tool
            user_id: ID of the authenticated user (for authorization)

        Returns:
            Result from the tool call
        """
        try:
            # Validate that the tool exists
            if tool_name not in self.server._tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }

            # Validate user_id format
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                return {
                    "success": False,
                    "error": "Invalid user_id format"
                }

            # Ensure user_id is included in arguments for authorization
            tool_arguments = arguments.copy()
            if "user_id" not in tool_arguments:
                tool_arguments["user_id"] = user_id

            # In a real implementation, we would call the tool through the MCP protocol
            # For now, we'll simulate the call by directly invoking the registered function
            tool = self.server._tools[tool_name]

            # Execute the tool function
            result = await tool.fn(tool_arguments)

            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def batch_call_tools(self, tool_calls: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls in sequence.

        Args:
            tool_calls: List of tool call dictionaries with name and arguments
            user_id: ID of the authenticated user

        Returns:
            List of results from the tool calls
        """
        results = []

        for tool_call in tool_calls:
            result = await self.call_tool(
                tool_name=tool_call["name"],
                arguments=tool_call["arguments"],
                user_id=user_id
            )
            results.append({
                "tool_call_id": tool_call.get("id", ""),
                "output": json.dumps(result)
            })

        return results


# Global tool caller instance
tool_caller = MCPTodoToolCaller()