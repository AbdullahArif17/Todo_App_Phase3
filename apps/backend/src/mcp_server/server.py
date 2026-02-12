import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import json
import uuid
from sqlmodel import Session

from mcp.server import Server
from mcp.types import Tool, CallToolResult, TextContent
from pydantic import BaseModel
from typing import Optional, List

from ..services.todo_service import TodoService
from ..database import engine


class AddTaskParams(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = ""


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


@asynccontextmanager
async def lifespan(server: Server):
    """Lifespan context manager for the MCP server."""
    # Initialize services
    todo_service = TodoService()

    # Define tools and register them
    tools = []

    # Add Task Tool
    add_task_tool = Tool(
        name="add_task",
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

    async def add_task_handler(arguments: Dict[str, Any]) -> CallToolResult:
        """Handler for add_task tool."""
        try:
            params = AddTaskParams(**arguments)

            # Validate user_id format
            try:
                user_uuid = uuid.UUID(params.user_id)
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "error": "Invalid UUID format for user_id"
                            })
                        )
                    ],
                    is_error=True
                )

            # Create task using TodoService
            with Session(engine) as session:
                from ..models.todo_task import TodoTaskCreate

                todo_create = TodoTaskCreate(
                    title=params.title,
                    description=params.description or "",
                    is_completed=False
                )

                # Create temporary user object
                from ..models.user import User
                temp_user = User(id=user_uuid, email="temp@example.com", is_active=True, hashed_password="temp")

                created_task = await todo_service.create_todo(todo_data=todo_create, user=temp_user, db_session=session)

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "message": f"Task '{params.title}' created successfully",
                                "task": {
                                    "id": str(created_task.id),
                                    "title": created_task.title,
                                    "description": created_task.description,
                                    "is_completed": created_task.is_completed
                                }
                            })
                        )
                    ],
                    is_error=False
                )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": str(e)
                        })
                    )
                ],
                is_error=True
            )

    # List Tasks Tool
    list_tasks_tool = Tool(
        name="list_tasks",
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

    async def list_tasks_handler(arguments: Dict[str, Any]) -> CallToolResult:
        """Handler for list_tasks tool."""
        try:
            params = ListTasksParams(**arguments)

            # Validate user_id format
            try:
                user_uuid = uuid.UUID(params.user_id)
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "error": "Invalid UUID format for user_id"
                            })
                        )
                    ],
                    is_error=True
                )

            # List tasks using TodoService
            with Session(engine) as session:
                from ..models.user import User

                # Create a temporary user object to pass to the service
                temp_user = User(id=user_uuid, email="temp@example.com", is_active=True, hashed_password="temp")

                tasks = await todo_service.get_user_todos(user=temp_user, db_session=session)

                # Apply limit and offset manually since the service doesn't support it yet
                limited_tasks = tasks[params.offset:params.offset + params.limit]

                tasks_list = [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "is_completed": task.is_completed
                    }
                    for task in limited_tasks
                ]

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "message": f"Retrieved {len(tasks_list)} tasks for user",
                                "tasks": tasks_list
                            })
                        )
                    ],
                    is_error=False
                )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": str(e)
                        })
                    )
                ],
                is_error=True
            )

    # Update Task Tool
    update_task_tool = Tool(
        name="update_task",
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

    async def update_task_handler(arguments: Dict[str, Any]) -> CallToolResult:
        """Handler for update_task tool."""
        try:
            params = UpdateTaskParams(**arguments)

            # Validate UUID formats
            try:
                user_uuid = uuid.UUID(params.user_id)
                task_uuid = uuid.UUID(params.task_id)
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "error": "Invalid UUID format for user_id or task_id"
                            })
                        )
                    ],
                    is_error=True
                )

            # Update task using TodoService
            with Session(engine) as session:
                from ..models.user import User
                from ..models.todo_task import TodoTaskUpdate

                # Create temporary user object
                temp_user = User(id=user_uuid, email="temp@example.com", is_active=True, hashed_password="temp")

                # Prepare update data
                update_data = {}
                if params.title is not None:
                    update_data["title"] = params.title
                if params.description is not None:
                    update_data["description"] = params.description
                if params.is_completed is not None:
                    update_data["is_completed"] = params.is_completed

                if not update_data:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": "No fields provided for update"
                                })
                            )
                        ],
                        is_error=True
                    )

                todo_update = TodoTaskUpdate(**update_data)
                updated_task = await todo_service.update_todo(
                    todo_id=task_uuid,
                    todo_update=todo_update,
                    user=temp_user,
                    db_session=session
                )

                if updated_task:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": True,
                                    "message": f"Task '{updated_task.title}' updated successfully",
                                    "task": {
                                        "id": str(updated_task.id),
                                        "title": updated_task.title,
                                        "description": updated_task.description,
                                        "is_completed": updated_task.is_completed
                                    }
                                })
                            )
                        ],
                        is_error=False
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": "Task not found or user not authorized to update"
                                })
                            )
                        ],
                        is_error=True
                    )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": str(e)
                        })
                    )
                ],
                is_error=True
            )

    # Complete Task Tool
    complete_task_tool = Tool(
        name="complete_task",
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

    async def complete_task_handler(arguments: Dict[str, Any]) -> CallToolResult:
        """Handler for complete_task tool."""
        try:
            params = CompleteTaskParams(**arguments)

            # Validate UUID formats
            try:
                user_uuid = uuid.UUID(params.user_id)
                task_uuid = uuid.UUID(params.task_id)
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "error": "Invalid UUID format for user_id or task_id"
                            })
                        )
                    ],
                    is_error=True
                )

            # Update task completion status using TodoService
            with Session(engine) as session:
                from ..models.user import User

                # Create temporary user object
                temp_user = User(id=user_uuid, email="temp@example.com", is_active=True, hashed_password="temp")

                updated_task = await todo_service.toggle_todo_completion(
                    todo_id=task_uuid,
                    is_completed=params.is_completed,
                    user=temp_user,
                    db_session=session
                )

                if updated_task:
                    status_text = "completed" if params.is_completed else "marked as incomplete"
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": True,
                                    "message": f"Task '{updated_task.title}' has been {status_text}",
                                    "task": {
                                        "id": str(updated_task.id),
                                        "title": updated_task.title,
                                        "description": updated_task.description,
                                        "is_completed": updated_task.is_completed
                                    }
                                })
                            )
                        ],
                        is_error=False
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": "Task not found or user not authorized to update"
                                })
                            )
                        ],
                        is_error=True
                    )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": str(e)
                        })
                    )
                ],
                is_error=True
            )

    # Delete Task Tool
    delete_task_tool = Tool(
        name="delete_task",
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

    async def delete_task_handler(arguments: Dict[str, Any]) -> CallToolResult:
        """Handler for delete_task tool."""
        try:
            params = DeleteTaskParams(**arguments)

            # Validate UUID formats
            try:
                user_uuid = uuid.UUID(params.user_id)
                task_uuid = uuid.UUID(params.task_id)
            except ValueError:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": False,
                                "error": "Invalid UUID format for user_id or task_id"
                            })
                        )
                    ],
                    is_error=True
                )

            # Delete task using TodoService
            with Session(engine) as session:
                from ..models.user import User

                # Create temporary user object
                temp_user = User(id=user_uuid, email="temp@example.com", is_active=True, hashed_password="temp")

                success = await todo_service.delete_todo(
                    todo_id=task_uuid,
                    user=temp_user,
                    db_session=session
                )

                if success:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": True,
                                    "message": "Task deleted successfully"
                                })
                            )
                        ],
                        is_error=False
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": "Task not found or user not authorized to delete"
                                })
                            )
                        ],
                        is_error=True
                    )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": str(e)
                        })
                    )
                ],
                is_error=True
            )

    # Register tools with the server
    server.add_tool(add_task_tool, add_task_handler)
    server.add_tool(list_tasks_tool, list_tasks_handler)
    server.add_tool(update_task_tool, update_task_handler)
    server.add_tool(complete_task_tool, complete_task_handler)
    server.add_tool(delete_task_tool, delete_task_handler)

    yield

    # Cleanup on shutdown
    pass


# Global server instance
mcp_todo_server = Server(
    name="todo-mcp-server",
    version="1.0.0",
    lifespan=lifespan
)