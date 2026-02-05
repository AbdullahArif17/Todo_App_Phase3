"""
AI Utilities for Todo Agent
Helper functions for agent context building and conversation management
"""

from typing import List, Dict, Any
from datetime import datetime

from apps.backend.src.models.message import Message
from apps.backend.src.models.conversation import Conversation


def build_agent_context(conversation: Conversation, messages: List[Message], user_id: str) -> str:
    """
    Build context for the AI agent based on conversation history.

    Args:
        conversation: The conversation object
        messages: List of messages in the conversation
        user_id: ID of the user

    Returns:
        Formatted string containing conversation context for the agent
    """
    context_parts = []

    # Add conversation header
    context_parts.append(f"=== CONVERSATION CONTEXT ===")
    context_parts.append(f"Conversation ID: {conversation.id}")
    context_parts.append(f"User ID: {user_id}")
    context_parts.append(f"Created: {conversation.created_at}")
    context_parts.append("")

    # Add message history
    context_parts.append("=== MESSAGE HISTORY ===")

    for message in messages:
        role_prefix = "USER" if message.role == "user" else "ASSISTANT"
        timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        context_parts.append(f"[{timestamp}] {role_prefix}: {message.content}")
        context_parts.append("")

    context_parts.append("=== END OF HISTORY ===")
    context_parts.append("")
    context_parts.append("Please continue this conversation by responding to the user's most recent message.")

    return "\n".join(context_parts)


def format_tool_response_for_agent(tool_result: Dict[str, Any]) -> str:
    """
    Format a tool response in a way that's useful for the AI agent.

    Args:
        tool_result: The result from a tool call

    Returns:
        Formatted string representation of the tool result
    """
    if not tool_result.get("success"):
        error_msg = tool_result.get("error", "Unknown error occurred")
        return f"Tool call failed: {error_msg}"

    result_data = tool_result.get("result", {})

    if "task" in result_data:
        task = result_data["task"]
        task_info = f"Task ID: {task.get('id')}\n"
        task_info += f"Title: {task.get('title')}\n"
        task_info += f"Completed: {task.get('is_completed', False)}\n"
        task_info += f"Description: {task.get('description', '')}"
        return f"Operation successful:\n{task_info}"

    elif "tasks" in result_data:
        tasks = result_data["tasks"]
        task_list = [f"- {task.get('title')} (ID: {task.get('id')})" for task in tasks]
        return f"Found {len(tasks)} tasks:\n" + "\n".join(task_list)

    else:
        return f"Operation completed successfully: {result_data.get('message', 'Success')}"


def extract_user_intent(user_message: str) -> Dict[str, Any]:
    """
    Extract intent from a user message (basic implementation).

    Args:
        user_message: The raw message from the user

    Returns:
        Dictionary with extracted intent information
    """
    message_lower = user_message.lower().strip()

    # Basic intent detection - in a real implementation, this would use more sophisticated NLP
    intent_data = {
        "raw_message": user_message,
        "detected_intent": "unknown",
        "entities": [],
        "confidence": 0.0
    }

    # Detect common intents
    if any(word in message_lower for word in ["add", "create", "new", "make"]):
        if any(word in message_lower for word in ["task", "todo", "item", "thing"]):
            intent_data["detected_intent"] = "add_task"

    elif any(word in message_lower for word in ["list", "show", "see", "display", "view", "get"]):
        if any(word in message_lower for word in ["task", "todo", "item", "things"]):
            intent_data["detected_intent"] = "list_tasks"

    elif any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
        if any(word in message_lower for word in ["task", "todo", "item"]):
            intent_data["detected_intent"] = "complete_task"

    elif any(word in message_lower for word in ["update", "change", "modify", "edit"]):
        if any(word in message_lower for word in ["task", "todo", "item"]):
            intent_data["detected_intent"] = "update_task"

    elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
        if any(word in message_lower for word in ["task", "todo", "item"]):
            intent_data["detected_intent"] = "delete_task"

    # Set confidence based on whether we detected an intent
    intent_data["confidence"] = 0.8 if intent_data["detected_intent"] != "unknown" else 0.2

    return intent_data


def prepare_agent_instructions(base_instructions: str, conversation_context: str) -> str:
    """
    Prepare complete instructions for the agent combining base instructions with conversation context.

    Args:
        base_instructions: The base system instructions for the agent
        conversation_context: Context from the conversation history

    Returns:
        Combined instructions for the agent
    """
    full_instructions = f"{base_instructions}\n\n"
    full_instructions += "CONVERSATION CONTEXT:\n"
    full_instructions += conversation_context
    full_instructions += "\n\nUSER REQUEST:"

    return full_instructions


def validate_agent_response(response: str, required_elements: List[str] = None) -> Dict[str, Any]:
    """
    Validate an agent response to ensure it meets certain criteria.

    Args:
        response: The response from the agent
        required_elements: List of elements that should be present in the response

    Returns:
        Validation results with pass/fail status and feedback
    """
    validation_result = {
        "is_valid": True,
        "feedback": [],
        "missing_elements": []
    }

    if required_elements:
        for element in required_elements:
            if element.lower() not in response.lower():
                validation_result["is_valid"] = False
                validation_result["missing_elements"].append(element)
                validation_result["feedback"].append(f"Missing required element: {element}")

    # Check for basic quality metrics
    if len(response.strip()) < 5:
        validation_result["is_valid"] = False
        validation_result["feedback"].append("Response is too short")

    if response.lower().startswith("i don't know") or response.lower().startswith("i cannot"):
        validation_result["is_valid"] = False
        validation_result["feedback"].append("Response indicates inability to help")

    return validation_result