"""
Todo Agent Implementation
Uses LLM provider (Groq or OpenAI) to create an AI agent that manages todos via MCP tools
"""
from groq import AsyncGroq
from typing import Dict, Any, List, Optional
import uuid
from sqlmodel import Session
from ..core.config import settings
from ..mcp_server.main import mcp_todo_server

class TodoAgent:
    """
    Todo Agent that uses LLM provider to manage todos via MCP tools.
    The agent is configured with system instructions and MCP tools for all operations.
    Supports both Groq and OpenAI providers based on configuration.
    """

    def __init__(self):
        # Initialize appropriate LLM client based on provider
        if settings.AI_PROVIDER.lower() == "groq":
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.model = settings.GROQ_MODEL
        else:  # Default to OpenAI
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL

        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS

    async def process_message_with_context(self, user_input: str, conversation_history: List[Dict[str, str]], session: Session = None) -> str:
        """
        Process user input with conversation history and return AI-generated response.

        Args:
            user_input: The user's message
            conversation_history: List of previous messages in the conversation
            session: Database session for tool operations

        Returns:
            AI-generated response
        """
        # Prepare the messages for the AI model
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful todo management assistant that helps users manage their tasks using natural language. "
                    "You can help create, update, delete, and list todos. You have access to tools for these operations. "
                    "Always respond in a friendly and helpful manner. "
                    "When the user wants to perform a todo operation, use the appropriate tool."
                )
            }
        ]

        # Add conversation history to maintain context
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add the current user input
        messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            # Call the appropriate API based on provider
            if settings.AI_PROVIDER.lower() == "groq":
                # Use Groq API
                response = await self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=[
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        }
                    ],
                    tool_choice="auto"
                )
            else:
                # Use OpenAI API
                from openai import AsyncOpenAI
                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

                response = await openai_client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=[
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        },
                        {
                            "type": "function",
                            "function": {
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
                        }
                    ],
                    tool_choice="auto"
                )

        except Exception as e:
            # Handle AI service unavailability
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                return "I'm sorry, but I'm currently unable to process your request due to authentication issues. Please contact the administrator."
            elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
                return "I'm sorry, but I've reached my usage limit and cannot process your request right now. Please try again later."
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                return "I'm sorry, but I'm experiencing connectivity issues and cannot process your request right now. Please try again later."
            else:
                return f"I'm sorry, I encountered an error processing your request: {str(e)}"

        # Process the response
        response_message = response.choices[0].message

        # Check if the model wanted to call a function
        tool_calls = response_message.tool_calls

        if tool_calls:
            # Send the info for each function call and function response to the model
            messages.append(response_message)  # extend conversation with assistant's reply

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments

                # Execute the function
                try:
                    import json
                    args_dict = json.loads(function_args)
                    
                    # Get user_id from arguments
                    user_id_str = args_dict.get("user_id")
                    if not user_id_str:
                        result = {"success": False, "message": "Missing user_id in tool arguments"}
                    else:
                        try:
                            user_uuid = uuid.UUID(user_id_str)
                            # Create a temporary user object for the service
                            from ..models.user import User
                            temp_user = User(id=user_uuid, email="temp@example.com", is_active=True, hashed_password="temp")
                            
                            # Initialize TodoService
                            from ..services.todo_service import TodoService
                            todo_service = TodoService()

                            if function_name == "add_task":
                                from ..models.todo_task import TodoTaskCreate
                                todo_data = TodoTaskCreate(
                                    title=args_dict.get("title"),
                                    description=args_dict.get("description", ""),
                                    is_completed=False
                                )
                                task = await todo_service.create_todo(todo_data, temp_user, session)
                                result = {
                                    "success": True, 
                                    "message": f"Task '{task.title}' added successfully",
                                    "task": {"id": str(task.id), "title": task.title, "is_completed": task.is_completed}
                                }
                            elif function_name == "list_tasks":
                                tasks = await todo_service.get_user_todos(temp_user, session)
                                # Apply limit/offset if provided
                                limit = args_dict.get("limit", 10)
                                offset = args_dict.get("offset", 0)
                                tasks_paged = tasks[offset:offset+limit]
                                result = {
                                    "success": True,
                                    "message": f"Retrieved {len(tasks_paged)} tasks",
                                    "tasks": [{"id": str(t.id), "title": t.title, "is_completed": t.is_completed} for t in tasks_paged]
                                }
                            elif function_name == "update_task":
                                from ..models.todo_task import TodoTaskUpdate
                                task_id = uuid.UUID(args_dict.get("task_id"))
                                todo_update = TodoTaskUpdate(
                                    title=args_dict.get("title"),
                                    description=args_dict.get("description"),
                                    is_completed=args_dict.get("is_completed")
                                )
                                task = await todo_service.update_todo(task_id, todo_update, temp_user, session)
                                if task:
                                    result = {"success": True, "message": "Task updated successfully", "task": {"id": str(task.id), "title": task.title}}
                                else:
                                    result = {"success": False, "message": "Task not found or access denied"}
                            elif function_name == "complete_task":
                                task_id = uuid.UUID(args_dict.get("task_id"))
                                is_completed = args_dict.get("is_completed", True)
                                task = await todo_service.toggle_todo_completion(task_id, is_completed, temp_user, session)
                                if task:
                                    status = "completed" if is_completed else "marked incomplete"
                                    result = {"success": True, "message": f"Task {status} successfully"}
                                else:
                                    result = {"success": False, "message": "Task not found or access denied"}
                            elif function_name == "delete_task":
                                task_id = uuid.UUID(args_dict.get("task_id"))
                                success = await todo_service.delete_todo(task_id, temp_user, session)
                                result = {"success": success, "message": "Task deleted successfully" if success else "Task not found or access denied"}
                            else:
                                result = {"success": False, "message": f"Unknown tool: {function_name}"}
                        except ValueError as e:
                            result = {"success": False, "message": f"Invalid ID format: {str(e)}"}
                except Exception as e:
                    result = {
                        "success": False,
                        "message": f"Error executing function {function_name}: {str(e)}"
                    }

                # Add function response to the messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(result)  # Result of the function call
                })

        # Get the final response from the model after function calls
            if settings.AI_PROVIDER.lower() == "groq":
                final_response = await self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
            else:
                # Use OpenAI for final response
                from openai import AsyncOpenAI
                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

                final_response = await openai_client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

            return final_response.choices[0].message.content

        else:
            # No tool calls were made, return the original response
            return response_message.content


todo_agent = TodoAgent()