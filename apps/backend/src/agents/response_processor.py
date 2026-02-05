"""
Agent Response Processor
Processes agent responses to provide both natural language responses and tool metadata
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """
    Structure for agent responses that includes both natural language and tool metadata
    """
    natural_language_response: str
    tool_calls: List[Dict[str, Any]] = []
    tool_results: List[Dict[str, Any]] = []
    action_metadata: Dict[str, Any] = {}
    needs_clarification: bool = False
    conversation_id: Optional[str] = None


class AgentResponseProcessor:
    """
    Processes responses from the AI agent to extract both natural language responses
    and structured tool metadata for application use.
    """

    def __init__(self):
        pass

    def process_response(self, raw_response: Dict[str, Any],
                         tool_calls: List[Dict[str, Any]] = None,
                         tool_results: List[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a raw agent response into a structured format.

        Args:
            raw_response: Raw response from the AI agent
            tool_calls: List of tools that were called during processing
            tool_results: Results from the tool calls

        Returns:
            Structured AgentResponse object
        """
        natural_language_response = self._extract_natural_language_response(raw_response)

        if tool_calls is None:
            tool_calls = []
        if tool_results is None:
            tool_results = []

        action_metadata = self._generate_action_metadata(tool_calls, tool_results)
        needs_clarification = self._detect_needs_clarification(natural_language_response)

        return AgentResponse(
            natural_language_response=natural_language_response,
            tool_calls=tool_calls,
            tool_results=tool_results,
            action_metadata=action_metadata,
            needs_clarification=needs_clarification
        )

    def _extract_natural_language_response(self, raw_response: Dict[str, Any]) -> str:
        """
        Extract the natural language response from the raw agent response.

        Args:
            raw_response: Raw response from the AI agent

        Returns:
            Natural language response text
        """
        # In the actual implementation, this would extract the text from the agent response
        # For now, we'll handle different response formats

        if isinstance(raw_response, str):
            return raw_response
        elif isinstance(raw_response, dict):
            # Look for common response keys
            if 'response_text' in raw_response:
                return raw_response['response_text']
            elif 'message' in raw_response:
                return raw_response['message']
            elif 'content' in raw_response:
                return raw_response['content']
            else:
                # If none found, convert the entire dict to string
                return str(raw_response)
        else:
            return str(raw_response)

    def _generate_action_metadata(self, tool_calls: List[Dict[str, Any]],
                                tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate metadata about the actions taken by the agent.

        Args:
            tool_calls: List of tools that were called
            tool_results: Results from the tool calls

        Returns:
            Action metadata dictionary
        """
        metadata = {
            "total_tool_calls": len(tool_calls),
            "successful_operations": 0,
            "failed_operations": 0,
            "operation_types": [],
            "timestamp": self._get_current_timestamp()
        }

        # Count successful and failed operations
        for result in tool_results:
            if result.get("success", False):
                metadata["successful_operations"] += 1
            else:
                metadata["failed_operations"] += 1

        # Collect operation types
        for call in tool_calls:
            tool_name = call.get("name", "unknown")
            if tool_name not in metadata["operation_types"]:
                metadata["operation_types"].append(tool_name)

        return metadata

    def _detect_needs_clarification(self, response: str) -> bool:
        """
        Detect if the agent response indicates that clarification is needed.

        Args:
            response: Natural language response from the agent

        Returns:
            True if clarification is needed, False otherwise
        """
        response_lower = response.lower()

        # Check for phrases indicating the agent needs clarification
        clarification_indicators = [
            "could you clarify",
            "can you clarify",
            "which one",
            "what do you mean",
            "more specific",
            "not sure which",
            "please specify",
            "which task",
            "unclear",
            "ambiguous"
        ]

        for indicator in clarification_indicators:
            if indicator in response_lower:
                return True

        return False

    def format_for_frontend(self, agent_response: AgentResponse) -> Dict[str, Any]:
        """
        Format the agent response for frontend consumption.

        Args:
            agent_response: Processed agent response

        Returns:
            Dictionary formatted for frontend consumption
        """
        return {
            "response": agent_response.natural_language_response,
            "tool_calls": agent_response.tool_calls,
            "action_metadata": agent_response.action_metadata,
            "needs_clarification": agent_response.needs_clarification,
            "timestamp": self._get_current_timestamp()
        }

    def format_for_logging(self, agent_response: AgentResponse, user_id: str,
                          conversation_id: str) -> Dict[str, Any]:
        """
        Format the agent response for logging purposes.

        Args:
            agent_response: Processed agent response
            user_id: ID of the user
            conversation_id: ID of the conversation

        Returns:
            Dictionary formatted for logging
        """
        return {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "natural_language_response_length": len(agent_response.natural_language_response),
            "tool_calls_count": len(agent_response.tool_calls),
            "successful_operations": agent_response.action_metadata.get("successful_operations", 0),
            "failed_operations": agent_response.action_metadata.get("failed_operations", 0),
            "operation_types": agent_response.action_metadata.get("operation_types", []),
            "needs_clarification": agent_response.needs_clarification,
            "timestamp": self._get_current_timestamp()
        }

    def _get_current_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.

        Returns:
            Current timestamp as ISO string
        """
        from datetime import datetime
        return datetime.now().isoformat()


class DualOutputFormatter:
    """
    Formatter that ensures responses include both natural language and tool metadata.
    """

    def format_with_confirmation(self, operation_result: Dict[str, Any],
                               user_request: str) -> AgentResponse:
        """
        Format a response that includes confirmation of an operation.

        Args:
            operation_result: Result from a tool operation
            user_request: Original user request

        Returns:
            AgentResponse with confirmation text and operation metadata
        """
        # Generate natural language confirmation based on operation result
        confirmation_text = self._generate_confirmation_text(operation_result, user_request)

        # Create tool calls and results based on the operation
        tool_calls = [{"name": operation_result.get("operation_type", "unknown"),
                      "arguments": operation_result.get("arguments", {})}]
        tool_results = [operation_result]

        # Process into agent response format
        processor = AgentResponseProcessor()
        return processor.process_response(
            raw_response={"response_text": confirmation_text},
            tool_calls=tool_calls,
            tool_results=tool_results
        )

    def _generate_confirmation_text(self, operation_result: Dict[str, Any],
                                   user_request: str) -> str:
        """
        Generate natural language confirmation text based on operation result.

        Args:
            operation_result: Result from a tool operation
            user_request: Original user request

        Returns:
            Natural language confirmation text
        """
        operation_type = operation_result.get("operation_type", "operation")
        success = operation_result.get("success", False)

        if success:
            if operation_type == "add_task":
                task_title = operation_result.get("result", {}).get("task", {}).get("title", "the task")
                return f"I've successfully added the task '{task_title}' to your list."
            elif operation_type == "list_tasks":
                task_count = len(operation_result.get("result", {}).get("tasks", []))
                return f"I found {task_count} tasks in your list."
            elif operation_type == "update_task":
                task_title = operation_result.get("result", {}).get("task", {}).get("title", "the task")
                return f"I've successfully updated the task '{task_title}'."
            elif operation_type == "complete_task":
                task_title = operation_result.get("result", {}).get("task", {}).get("title", "the task")
                status = "completed" if operation_result.get("result", {}).get("task", {}).get("is_completed", False) else "marked as incomplete"
                return f"I've successfully {status} the task '{task_title}'."
            elif operation_type == "delete_task":
                return "I've successfully deleted the task."
            else:
                return f"I've successfully completed the {operation_type}."
        else:
            error_msg = operation_result.get("error", "an error occurred")
            return f"I'm sorry, but I encountered an issue: {error_msg}. Could you please try again?"


# Global response processor instance
response_processor = AgentResponseProcessor()
dual_output_formatter = DualOutputFormatter()