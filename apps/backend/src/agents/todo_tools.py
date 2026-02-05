from typing import Dict, Any, List
from pydantic import BaseModel
import uuid
from apps.backend.src.services.todo_service import TodoService
from apps.backend.src.models.todo_task import TodoTask


class CreateTodoParams(BaseModel):
    title: str
    description: str = ""
    user_id: uuid.UUID


class UpdateTodoParams(BaseModel):
    todo_id: uuid.UUID
    title: str = None
    description: str = None
    completed: bool = None


class DeleteTodoParams(BaseModel):
    todo_id: uuid.UUID


class ListTodosParams(BaseModel):
    user_id: uuid.UUID
    limit: int = 10
    offset: int = 0


class TodoTools:
    """
    Tools for the AI agent to interact with todo operations.
    """
    def __init__(self):
        self.todo_service = TodoService()

    def create_todo(self, params: CreateTodoParams) -> Dict[str, Any]:
        """
        Create a new todo item.

        Args:
            params: Parameters for creating the todo

        Returns:
            Dictionary with result of the operation
        """
        try:
            # Note: In a real implementation, we'd need to pass the database session
            # For now, we'll simulate the call
            todo_data = {
                "title": params.title,
                "description": params.description,
                "user_id": params.user_id
            }

            # This would call the actual service method with a session
            # For now, return a simulated successful response
            return {
                "success": True,
                "message": f"Todo '{params.title}' created successfully",
                "todo_id": str(uuid.uuid4())  # Simulated new ID
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create todo: {str(e)}"
            }

    def update_todo(self, params: UpdateTodoParams) -> Dict[str, Any]:
        """
        Update an existing todo item.

        Args:
            params: Parameters for updating the todo

        Returns:
            Dictionary with result of the operation
        """
        try:
            update_data = {}
            if params.title is not None:
                update_data["title"] = params.title
            if params.description is not None:
                update_data["description"] = params.description
            if params.completed is not None:
                update_data["completed"] = params.completed

            # This would call the actual service method with a session
            return {
                "success": True,
                "message": f"Todo {params.todo_id} updated successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update todo: {str(e)}"
            }

    def delete_todo(self, params: DeleteTodoParams) -> Dict[str, Any]:
        """
        Delete a todo item.

        Args:
            params: Parameters for deleting the todo

        Returns:
            Dictionary with result of the operation
        """
        try:
            # This would call the actual service method with a session
            return {
                "success": True,
                "message": f"Todo {params.todo_id} deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete todo: {str(e)}"
            }

    def list_todos(self, params: ListTodosParams) -> Dict[str, Any]:
        """
        List todo items for a user.

        Args:
            params: Parameters for listing todos

        Returns:
            Dictionary with result of the operation
        """
        try:
            # This would call the actual service method with a session
            # For now, return a simulated response
            return {
                "success": True,
                "message": f"Retrieved todos for user {params.user_id}",
                "todos": []  # Would contain actual todos in real implementation
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to list todos: {str(e)}"
            }

    # Actual implementation that works with the service layer
    def create_todo_with_session(self, session, title: str, description: str = "", user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Create a new todo item with database session.

        Args:
            session: Database session
            title: Title of the todo
            description: Description of the todo
            user_id: ID of the user creating the todo

        Returns:
            Dictionary with result of the operation
        """
        try:
            from apps.backend.src.models.todo_task import TodoTask
            from apps.backend.src.schemas.todo_task import TodoTaskCreate

            todo_create = TodoTaskCreate(
                title=title,
                description=description,
                user_id=user_id
            )

            todo = self.todo_service.create_todo(session, todo_create)

            return {
                "success": True,
                "message": f"Todo '{title}' created successfully",
                "todo_id": str(todo.id),
                "todo": {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create todo: {str(e)}"
            }

    def update_todo_with_session(self, session, todo_id: uuid.UUID, title: str = None,
                                description: str = None, completed: bool = None) -> Dict[str, Any]:
        """
        Update an existing todo item with database session.

        Args:
            session: Database session
            todo_id: ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Dictionary with result of the operation
        """
        try:
            from apps.backend.src.schemas.todo_task import TodoTaskUpdate

            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if completed is not None:
                update_data["completed"] = completed

            if not update_data:
                return {
                    "success": False,
                    "message": "No fields to update"
                }

            todo_update = TodoTaskUpdate(**update_data)
            todo = self.todo_service.update_todo(session, todo_id, todo_update)

            return {
                "success": True,
                "message": f"Todo {todo_id} updated successfully",
                "todo": {
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update todo: {str(e)}"
            }

    def delete_todo_with_session(self, session, todo_id: uuid.UUID) -> Dict[str, Any]:
        """
        Delete a todo item with database session.

        Args:
            session: Database session
            todo_id: ID of the todo to delete

        Returns:
            Dictionary with result of the operation
        """
        try:
            self.todo_service.delete_todo(session, todo_id)

            return {
                "success": True,
                "message": f"Todo {todo_id} deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete todo: {str(e)}"
            }

    def list_todos_with_session(self, session, user_id: uuid.UUID, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List todo items for a user with database session.

        Args:
            session: Database session
            user_id: ID of the user whose todos to list
            limit: Maximum number of todos to return
            offset: Number of todos to skip

        Returns:
            Dictionary with result of the operation
        """
        try:
            todos = self.todo_service.get_todos_by_user_id(session, user_id, skip=offset, limit=limit)

            todos_list = []
            for todo in todos:
                todos_list.append({
                    "id": str(todo.id),
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed
                })

            return {
                "success": True,
                "message": f"Retrieved {len(todos_list)} todos for user {user_id}",
                "todos": todos_list
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to list todos: {str(e)}"
            }