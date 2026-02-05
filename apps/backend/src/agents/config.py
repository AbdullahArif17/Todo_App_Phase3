"""
Configuration for Todo Agent
Defines system instructions and agent settings for the OpenAI Agent
"""
from pydantic import BaseModel
from typing import Dict, Any


class AgentConfig(BaseModel):
    """
    Configuration settings for the Todo Agent
    """
    name: str = "Todo Assistant"
    model: str = "gpt-4-turbo"
    temperature: float = 0.7
    instructions: str = (
        "You are a helpful todo management assistant that helps users manage their tasks using natural language. "
        "Follow these rules:\n\n"

        "1. ONLY use the provided tools for all todo operations.\n"
        "2. Never directly access or modify data yourself.\n"
        "3. Always respond in a friendly and helpful tone.\n"
        "4. If a user wants to perform an action but doesn't specify a particular task, "
        "ask for clarification or suggest listing existing tasks first.\n"
        "5. When a user refers to a task that might be ambiguous, ask for clarification "
        "rather than guessing.\n"
        "6. For complex operations (like updating or deleting), you may need to call multiple "
        "tools in sequence (e.g., list tasks first, then perform the operation).\n"
        "7. Always respect the user's privacy and only access tasks that belong to them.\n"
        "8. If you encounter an error, explain it to the user in a helpful way and suggest alternatives."
    )


class ToolConfig(BaseModel):
    """
    Configuration for available tools
    """
    add_task: Dict[str, Any] = {
        "name": "add_task",
        "description": "Add a new task for a user. Requires user_id and title.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The ID of the user creating the task"},
                "title": {"type": "string", "description": "The title of the task to create"},
                "description": {"type": "string", "description": "Optional description of the task"}
            },
            "required": ["user_id", "title"]
        }
    }

    list_tasks: Dict[str, Any] = {
        "name": "list_tasks",
        "description": "List tasks for a user. Requires user_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The ID of the user whose tasks to list"},
                "limit": {"type": "integer", "description": "Maximum number of tasks to return (default: 10)"},
                "offset": {"type": "integer", "description": "Number of tasks to skip (default: 0)"}
            },
            "required": ["user_id"]
        }
    }

    update_task: Dict[str, Any] = {
        "name": "update_task",
        "description": "Update an existing task for a user. Requires user_id and task_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The ID of the user"},
                "task_id": {"type": "string", "description": "The ID of the task to update"},
                "title": {"type": "string", "description": "New title for the task (optional)"},
                "description": {"type": "string", "description": "New description for the task (optional)"},
                "is_completed": {"type": "boolean", "description": "New completion status for the task (optional)"}
            },
            "required": ["user_id", "task_id"]
        }
    }

    complete_task: Dict[str, Any] = {
        "name": "complete_task",
        "description": "Mark a task as complete or incomplete for a user. Requires user_id and task_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The ID of the user"},
                "task_id": {"type": "string", "description": "The ID of the task to update"},
                "is_completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"}
            },
            "required": ["user_id", "task_id"]
        }
    }

    delete_task: Dict[str, Any] = {
        "name": "delete_task",
        "description": "Delete a task for a user. Requires user_id and task_id.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The ID of the user"},
                "task_id": {"type": "string", "description": "The ID of the task to delete"}
            },
            "required": ["user_id", "task_id"]
        }
    }


# Global configuration instances
agent_config = AgentConfig()
tool_config = ToolConfig()