"""
MCP Tools for Todo Operations
Implements the required todo operation tools for AI agents using the Official MCP SDK
"""
from mcp.types import ToolResult
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from sqlmodel import Session

from apps.backend.src.services.todo_service import TodoService
from apps.backend.src.database import engine


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


class MCPTodoTools:
    """
    MCP Tools implementation for todo operations that integrate with the existing backend services.
    Each tool enforces user ownership validation and returns structured responses for agent reasoning.
    """

    def __init__(self):
        self.todo_service = TodoService()

    def add_task(self, params: AddTaskParams, db_session: Session) -> ToolResult:
        """
        Add a new task for a user.

        Args:
            params: Parameters including user_id, title, and optional description
            db_session: Database session for the operation

        Returns:
            ToolResult with the created task information
        """
        try:
            # Validate user_id format
            user_uuid = uuid.UUID(params.user_id)
        except ValueError:
            return ToolResult(
                content={"error": "Invalid UUID format for user_id"},
                is_error=True
            )

        try:
            # Create the todo using the existing service
            from apps.backend.src.schemas.todo_task import TodoTaskCreate

            todo_create = TodoTaskCreate(
                title=params.title,
                description=params.description,
                is_completed=False
            )

            created_todo = self.todo_service.create_todo(
                session=db_session,
                user_id=user_uuid,
                todo_create=todo_create
            )

            return ToolResult(
                content={
                    "success": True,
                    "message": f"Task '{params.title}' added successfully",
                    "task": {
                        "id": str(created_todo.id),
                        "title": created_todo.title,
                        "description": created_todo.description,
                        "is_completed": created_todo.is_completed,
                        "created_at": created_todo.created_at.isoformat()
                    }
                },
                is_error=False
            )
        except Exception as e:
            return ToolResult(
                content={
                    "success": False,
                    "error": f"Failed to add task: {str(e)}"
                },
                is_error=True
            )

    def list_tasks(self, params: ListTasksParams, db_session: Session) -> ToolResult:
        """
        List tasks for a user.

        Args:
            params: Parameters including user_id with optional limit and offset
            db_session: Database session for the operation

        Returns:
            ToolResult with the list of tasks
        """
        try:
            # Validate user_id format
            user_uuid = uuid.UUID(params.user_id)
        except ValueError:
            return ToolResult(
                content={"error": "Invalid UUID format for user_id"},
                is_error=True
            )

        try:
            # Get todos for the user using the existing service
            todos = self.todo_service.get_todos_by_user_id(
                session=db_session,
                user_id=user_uuid,
                skip=params.offset,
                limit=params.limit
            )

            tasks_list = []
            for todo in todos:
                tasks_list.append({
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "is_completed": todo.is_completed,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                })

            return ToolResult(
                content={
                    "success": True,
                    "message": f"Retrieved {len(tasks_list)} tasks for user",
                    "tasks": tasks_list
                },
                is_error=False
            )
        except Exception as e:
            return ToolResult(
                content={
                    "success": False,
                    "error": f"Failed to list tasks: {str(e)}"
                },
                is_error=True
            )

    def update_task(self, params: UpdateTaskParams, db_session: Session) -> ToolResult:
        """
        Update a task for a user.

        Args:
            params: Parameters including user_id, task_id, and optional fields to update
            db_session: Database session for the operation

        Returns:
            ToolResult with the updated task information
        """
        try:
            # Validate UUID formats
            user_uuid = uuid.UUID(params.user_id)
            task_uuid = uuid.UUID(params.task_id)
        except ValueError:
            return ToolResult(
                content={"error": "Invalid UUID format for user_id or task_id"},
                is_error=True
            )

        try:
            # Check if the task exists and belongs to the user
            from apps.backend.src.models.todo_task import TodoTask
            from sqlmodel import select

            statement = select(TodoTask).where(
                TodoTask.id == task_uuid,
                TodoTask.user_id == user_uuid
            )
            existing_todo = db_session.exec(statement).first()

            if not existing_todo:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "Task not found or does not belong to user"
                    },
                    is_error=True
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
                    },
                    is_error=True
                )

            # Create update object and update the task
            todo_update = TodoTaskUpdate(**update_data)
            updated_todo = self.todo_service.update_todo(
                session=db_session,
                todo_id=task_uuid,
                todo_update=todo_update
            )

            return ToolResult(
                content={
                    "success": True,
                    "message": f"Task '{updated_todo.title}' updated successfully",
                    "task": {
                        "id": str(updated_todo.id),
                        "title": updated_todo.title,
                        "description": updated_todo.description,
                        "is_completed": updated_todo.is_completed,
                        "updated_at": updated_todo.updated_at.isoformat()
                    }
                },
                is_error=False
            )
        except Exception as e:
            return ToolResult(
                content={
                    "success": False,
                    "error": f"Failed to update task: {str(e)}"
                },
                is_error=True
            )

    def complete_task(self, params: CompleteTaskParams, db_session: Session) -> ToolResult:
        """
        Mark a task as complete/incomplete for a user.

        Args:
            params: Parameters including user_id, task_id, and completion status
            db_session: Database session for the operation

        Returns:
            ToolResult with the updated task information
        """
        try:
            # Validate UUID formats
            user_uuid = uuid.UUID(params.user_id)
            task_uuid = uuid.UUID(params.task_id)
        except ValueError:
            return ToolResult(
                content={"error": "Invalid UUID format for user_id or task_id"},
                is_error=True
            )

        try:
            # Check if the task exists and belongs to the user
            from apps.backend.src.models.todo_task import TodoTask
            from sqlmodel import select

            statement = select(TodoTask).where(
                TodoTask.id == task_uuid,
                TodoTask.user_id == user_uuid
            )
            existing_todo = db_session.exec(statement).first()

            if not existing_todo:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "Task not found or does not belong to user"
                    },
                    is_error=True
                )

            # Update completion status
            from apps.backend.src.schemas.todo_task import TodoTaskUpdate
            todo_update = TodoTaskUpdate(is_completed=params.is_completed)
            updated_todo = self.todo_service.update_todo(
                session=db_session,
                todo_id=task_uuid,
                todo_update=todo_update
            )

            status_text = "completed" if params.is_completed else "marked as incomplete"
            return ToolResult(
                content={
                    "success": True,
                    "message": f"Task '{updated_todo.title}' has been {status_text}",
                    "task": {
                        "id": str(updated_todo.id),
                        "title": updated_todo.title,
                        "description": updated_todo.description,
                        "is_completed": updated_todo.is_completed,
                        "updated_at": updated_todo.updated_at.isoformat()
                    }
                },
                is_error=False
            )
        except Exception as e:
            return ToolResult(
                content={
                    "success": False,
                    "error": f"Failed to update task completion: {str(e)}"
                },
                is_error=True
            )

    def delete_task(self, params: DeleteTaskParams, db_session: Session) -> ToolResult:
        """
        Delete a task for a user.

        Args:
            params: Parameters including user_id and task_id
            db_session: Database session for the operation

        Returns:
            ToolResult with operation result
        """
        try:
            # Validate UUID formats
            user_uuid = uuid.UUID(params.user_id)
            task_uuid = uuid.UUID(params.task_id)
        except ValueError:
            return ToolResult(
                content={"error": "Invalid UUID format for user_id or task_id"},
                is_error=True
            )

        try:
            # Check if the task exists and belongs to the user
            from apps.backend.src.models.todo_task import TodoTask
            from sqlmodel import select

            statement = select(TodoTask).where(
                TodoTask.id == task_uuid,
                TodoTask.user_id == user_uuid
            )
            existing_todo = db_session.exec(statement).first()

            if not existing_todo:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "Task not found or does not belong to user"
                    },
                    is_error=True
                )

            # Delete the task
            success = self.todo_service.delete_todo(
                session=db_session,
                todo_id=task_uuid
            )

            if success:
                return ToolResult(
                    content={
                        "success": True,
                        "message": "Task deleted successfully"
                    },
                    is_error=False
                )
            else:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "Failed to delete task"
                    },
                    is_error=True
                )
        except Exception as e:
            return ToolResult(
                content={
                    "success": False,
                    "error": f"Failed to delete task: {str(e)}"
                },
                is_error=True
            )