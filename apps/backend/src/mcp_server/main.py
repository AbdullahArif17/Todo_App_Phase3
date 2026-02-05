"""
MCP Server for Todo Operations
Implements the Official MCP SDK to expose todo operations as tools for AI agents
"""
from mcp.server import Server
from mcp.types import ToolResult
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import uuid
from sqlmodel import Session

from apps.backend.src.services.todo_service import TodoService
from apps.backend.src.database import engine
import uuid


class AddTaskParams(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None


class ListTasksParams(BaseModel):
    user_id: str
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class UpdateTaskParams(BaseModel):
    user_id: str
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class CompleteTaskParams(BaseModel):
    user_id: str
    task_id: str
    is_completed: bool = True


class DeleteTaskParams(BaseModel):
    user_id: str
    task_id: str


class MCPTodoServer:
    """
    MCP Server implementation that exposes todo operations as standardized tools for AI agents.
    """

    def __init__(self):
        self.server = Server(
            name="todo-mcp-server",
            version="1.0.0"
        )
        self.todo_service = TodoService()

        # Register all tools
        self._register_tools()

    def _register_tools(self):
        """Register all required MCP tools."""

        @self.server.tool(
            "add_task",
            description="Add a new task for a user. Requires user_id and title.",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user creating the task"},
                    "title": {"type": "string", "description": "The title of the task to create"},
                    "description": {"type": "string", "description": "Optional description of the task"}
                },
                "required": ["user_id", "title"]
            }
        )
        async def add_task_handler(arguments: Dict[str, Any]) -> ToolResult:
            """Handler for add_task tool."""
            try:
                params = AddTaskParams(**arguments)

                # Validate user_id format
                user_uuid = uuid.UUID(params.user_id)

                # Create task using TodoService
                with Session(engine) as session:
                    from apps.backend.src.schemas.todo_task import TodoTaskCreate

                    todo_create = TodoTaskCreate(
                        title=params.title,
                        description=params.description or "",
                        is_completed=False
                    )

                    created_task = self.todo_service.create_todo(session, user_uuid, todo_create)

                    return ToolResult(
                        content={
                            "success": True,
                            "message": f"Task '{params.title}' created successfully",
                            "task": {
                                "id": str(created_task.id),
                                "title": created_task.title,
                                "description": created_task.description,
                                "is_completed": created_task.is_completed
                            }
                        }
                    )
            except Exception as e:
                return ToolResult(
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )

        @self.server.tool(
            "list_tasks",
            description="List tasks for a user. Requires user_id.",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user whose tasks to list"},
                    "limit": {"type": "integer", "description": "Maximum number of tasks to return (default: 10)"},
                    "offset": {"type": "integer", "description": "Number of tasks to skip (default: 0)"}
                },
                "required": ["user_id"]
            }
        )
        async def list_tasks_handler(arguments: Dict[str, Any]) -> ToolResult:
            """Handler for list_tasks tool."""
            try:
                params = ListTasksParams(**arguments)

                # Validate user_id format
                user_uuid = uuid.UUID(params.user_id)

                # List tasks using TodoService
                with Session(engine) as session:
                    tasks = self.todo_service.get_todos_by_user_id(
                        session,
                        user_uuid,
                        skip=params.offset,
                        limit=params.limit
                    )

                    tasks_list = [
                        {
                            "id": str(task.id),
                            "title": task.title,
                            "description": task.description,
                            "is_completed": task.is_completed
                        }
                        for task in tasks
                    ]

                    return ToolResult(
                        content={
                            "success": True,
                            "message": f"Retrieved {len(tasks_list)} tasks for user",
                            "tasks": tasks_list
                        }
                    )
            except Exception as e:
                return ToolResult(
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )

        @self.server.tool(
            "update_task",
            description="Update an existing task for a user. Requires user_id and task_id.",
            input_schema={
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
        )
        async def update_task_handler(arguments: Dict[str, Any]) -> ToolResult:
            """Handler for update_task tool."""
            try:
                params = UpdateTaskParams(**arguments)

                # Validate UUID formats
                user_uuid = uuid.UUID(params.user_id)
                task_uuid = uuid.UUID(params.task_id)

                # Update task using TodoService
                with Session(engine) as session:
                    # First, get the existing task to check ownership
                    existing_task = self.todo_service.get_todo_by_id(session, task_uuid, user_uuid)
                    if not existing_task:
                        return ToolResult(
                            content={
                                "success": False,
                                "error": "Task not found or does not belong to user"
                            }
                        )

                    # Prepare update data
                    from apps.backend.src.schemas.todo_task import TodoTaskUpdate
                    update_data = {}
                    if params.title is not None:
                        update_data["title"] = params.title
                    if params.description is not None:
                        update_data["description"] = params.description
                    if params.is_completed is not None:
                        update_data["is_completed"] = params.is_completed

                    if not update_data:
                        return ToolResult(
                            content={
                                "success": False,
                                "error": "No fields provided for update"
                            }
                        )

                    todo_update = TodoTaskUpdate(**update_data)
                    updated_task = self.todo_service.update_todo(session, task_uuid, user_uuid, todo_update)

                    return ToolResult(
                        content={
                            "success": True,
                            "message": f"Task '{updated_task.title}' updated successfully",
                            "task": {
                                "id": str(updated_task.id),
                                "title": updated_task.title,
                                "description": updated_task.description,
                                "is_completed": updated_task.is_completed
                            }
                        }
                    )
            except Exception as e:
                return ToolResult(
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )

        @self.server.tool(
            "complete_task",
            description="Mark a task as complete or incomplete for a user. Requires user_id and task_id.",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user"},
                    "task_id": {"type": "string", "description": "The ID of the task to update"},
                    "is_completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"}
                },
                "required": ["user_id", "task_id"]
            }
        )
        async def complete_task_handler(arguments: Dict[str, Any]) -> ToolResult:
            """Handler for complete_task tool."""
            try:
                params = CompleteTaskParams(**arguments)

                # Validate UUID formats
                user_uuid = uuid.UUID(params.user_id)
                task_uuid = uuid.UUID(params.task_id)

                # Update task completion status using TodoService
                with Session(engine) as session:
                    # First, get the existing task to check ownership
                    existing_task = self.todo_service.get_todo_by_id(session, task_uuid, user_uuid)
                    if not existing_task:
                        return ToolResult(
                            content={
                                "success": False,
                                "error": "Task not found or does not belong to user"
                            }
                        )

                    # Update completion status
                    from apps.backend.src.schemas.todo_task import TodoTaskUpdate
                    todo_update = TodoTaskUpdate(is_completed=params.is_completed)
                    updated_task = self.todo_service.update_todo(session, task_uuid, user_uuid, todo_update)

                    status_text = "completed" if params.is_completed else "marked as incomplete"
                    return ToolResult(
                        content={
                            "success": True,
                            "message": f"Task '{updated_task.title}' has been {status_text}",
                            "task": {
                                "id": str(updated_task.id),
                                "title": updated_task.title,
                                "description": updated_task.description,
                                "is_completed": updated_task.is_completed
                            }
                        }
                    )
            except Exception as e:
                return ToolResult(
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )

        @self.server.tool(
            "delete_task",
            description="Delete a task for a user. Requires user_id and task_id.",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user"},
                    "task_id": {"type": "string", "description": "The ID of the task to delete"}
                },
                "required": ["user_id", "task_id"]
            }
        )
        async def delete_task_handler(arguments: Dict[str, Any]) -> ToolResult:
            """Handler for delete_task tool."""
            try:
                params = DeleteTaskParams(**arguments)

                # Validate UUID formats
                user_uuid = uuid.UUID(params.user_id)
                task_uuid = uuid.UUID(params.task_id)

                # Delete task using TodoService
                with Session(engine) as session:
                    # First, verify the task exists and belongs to the user
                    existing_task = self.todo_service.get_todo_by_id(session, task_uuid, user_uuid)
                    if not existing_task:
                        return ToolResult(
                            content={
                                "success": False,
                                "error": "Task not found or does not belong to user"
                            }
                        )

                    success = self.todo_service.delete_todo(session, task_uuid, user_uuid)

                    if success:
                        return ToolResult(
                            content={
                                "success": True,
                                "message": "Task deleted successfully"
                            }
                        )
                    else:
                        return ToolResult(
                            content={
                                "success": False,
                                "error": "Failed to delete task"
                            }
                        )
            except Exception as e:
                return ToolResult(
                    content={
                        "success": False,
                        "error": str(e)
                    }
                )

    def get_server(self):
        """Get the configured MCP server instance."""
        return self.server


# Global server instance
mcp_todo_server = MCPTodoServer()