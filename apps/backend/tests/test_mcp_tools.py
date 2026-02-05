"""
Unit Tests for MCP Tools
Tests to verify individual functionality of each MCP tool
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session
from apps.backend.src.mcp_server.tools.todo_tools import MCPTodoTools
from apps.backend.src.mcp_server.auth import validate_user_id_param
from apps.backend.src.models.user import User
from apps.backend.src.models.todo_task import TodoTask
from mcp.types import ToolResult
import uuid


def test_mcp_todo_tools_initialization():
    """Test that MCPTodoTools initializes correctly."""
    tools = MCPTodoTools()
    assert tools.todo_service is not None


def test_add_task_success():
    """Test successful add_task operation."""
    tools = MCPTodoTools()

    # Create valid parameters
    user_id = str(uuid.uuid4())
    params = tools.AddTaskParams(
        user_id=user_id,
        title="Test Task",
        description="Test Description"
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = uuid.uuid4()
    mock_todo.title = "Test Task"
    mock_todo.description = "Test Description"
    mock_todo.is_completed = False

    # Mock the todo service
    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        result = tools.add_task(params, mock_session)

    # Verify the result
    assert not result.is_error
    assert result.content["success"] is True
    assert result.content["message"].startswith("Task 'Test Task' added successfully")
    assert "task" in result.content
    assert result.content["task"]["id"] == str(mock_todo.id)
    assert result.content["task"]["title"] == "Test Task"


def test_add_task_invalid_user_id():
    """Test add_task with invalid user_id format."""
    tools = MCPTodoTools()

    # Create parameters with invalid UUID format
    params = tools.AddTaskParams(
        user_id="invalid-uuid-format",
        title="Test Task"
    )

    mock_session = Mock(spec=Session)
    result = tools.add_task(params, mock_session)

    # Should return an error
    assert result.is_error
    assert "error" in result.content


def test_add_task_service_error():
    """Test add_task when the service throws an exception."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    params = tools.AddTaskParams(
        user_id=user_id,
        title="Test Task"
    )

    mock_session = Mock(spec=Session)

    # Mock the service to raise an exception
    with patch.object(tools.todo_service, 'create_todo', side_effect=Exception("DB Error")):
        result = tools.add_task(params, mock_session)

    # Should return an error
    assert result.is_error
    assert "error" in result.content
    assert "DB Error" in result.content["error"]


def test_list_tasks_success():
    """Test successful list_tasks operation."""
    tools = MCPTodoTools()

    # Create valid parameters
    user_id = str(uuid.uuid4())
    params = tools.ListTasksParams(
        user_id=user_id,
        limit=5,
        offset=0
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the returned todos
    mock_todos = [
        Mock(spec=TodoTask),
        Mock(spec=TodoTask)
    ]
    mock_todos[0].id = uuid.uuid4()
    mock_todos[0].title = "Task 1"
    mock_todos[0].description = "Description 1"
    mock_todos[0].is_completed = False
    mock_todos[1].id = uuid.uuid4()
    mock_todos[1].title = "Task 2"
    mock_todos[1].description = "Description 2"
    mock_todos[1].is_completed = True

    # Mock the todo service
    with patch.object(tools.todo_service, 'get_todos_by_user_id', return_value=mock_todos):
        result = tools.list_tasks(params, mock_session)

    # Verify the result
    assert not result.is_error
    assert result.content["success"] is True
    assert result.content["message"].startswith("Retrieved 2 tasks for user")
    assert len(result.content["tasks"]) == 2
    assert result.content["tasks"][0]["title"] == "Task 1"
    assert result.content["tasks"][1]["title"] == "Task 2"


def test_list_tasks_invalid_user_id():
    """Test list_tasks with invalid user_id format."""
    tools = MCPTodoTools()

    # Create parameters with invalid UUID format
    params = tools.ListTasksParams(user_id="invalid-uuid-format")

    mock_session = Mock(spec=Session)
    result = tools.list_tasks(params, mock_session)

    # Should return an error
    assert result.is_error
    assert "error" in result.content


def test_update_task_success():
    """Test successful update_task operation."""
    tools = MCPTodoTools()

    # Create valid parameters
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=task_id,
        title="Updated Title",
        description="Updated Description",
        is_completed=True
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the updated todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = uuid.UUID(task_id)
    mock_todo.title = "Updated Title"
    mock_todo.description = "Updated Description"
    mock_todo.is_completed = True

    # Mock the todo service
    with patch.object(tools.todo_service, 'update_todo', return_value=mock_todo):
        result = tools.update_task(params, mock_session)

    # Verify the result
    assert not result.is_error
    assert result.content["success"] is True
    assert result.content["message"].startswith("Task 'Updated Title' updated successfully")
    assert "task" in result.content
    assert result.content["task"]["title"] == "Updated Title"


def test_update_task_no_fields_provided():
    """Test update_task when no update fields are provided."""
    tools = MCPTodoTools()

    # Create parameters with no update fields
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=task_id
    )

    mock_session = Mock(spec=Session)
    result = tools.update_task(params, mock_session)

    # Should return an error
    assert result.is_error
    assert "error" in result.content
    assert "No fields provided for update" in result.content["error"]


def test_update_task_invalid_uuids():
    """Test update_task with invalid UUID formats."""
    tools = MCPTodoTools()

    # Create parameters with invalid UUID formats
    params = tools.UpdateTaskParams(
        user_id="invalid-uuid",
        task_id="invalid-task-id"
    )

    mock_session = Mock(spec=Session)
    result = tools.update_task(params, mock_session)

    # Should return an error
    assert result.is_error
    assert "error" in result.content


def test_complete_task_success():
    """Test successful complete_task operation."""
    tools = MCPTodoTools()

    # Create valid parameters
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    params = tools.CompleteTaskParams(
        user_id=user_id,
        task_id=task_id,
        is_completed=True
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the updated todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = uuid.UUID(task_id)
    mock_todo.title = "Test Task"
    mock_todo.description = "Test Description"
    mock_todo.is_completed = True

    # Mock the todo service
    with patch.object(tools.todo_service, 'update_todo', return_value=mock_todo):
        result = tools.complete_task(params, mock_session)

    # Verify the result
    assert not result.is_error
    assert result.content["success"] is True
    assert "completed" in result.content["message"]
    assert "task" in result.content
    assert result.content["task"]["is_completed"] is True


def test_complete_task_mark_incomplete():
    """Test successful complete_task operation to mark incomplete."""
    tools = MCPTodoTools()

    # Create valid parameters to mark incomplete
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    params = tools.CompleteTaskParams(
        user_id=user_id,
        task_id=task_id,
        is_completed=False
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the updated todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = uuid.UUID(task_id)
    mock_todo.title = "Test Task"
    mock_todo.description = "Test Description"
    mock_todo.is_completed = False

    # Mock the todo service
    with patch.object(tools.todo_service, 'update_todo', return_value=mock_todo):
        result = tools.complete_task(params, mock_session)

    # Verify the result
    assert not result.is_error
    assert result.content["success"] is True
    assert "marked as incomplete" in result.content["message"]
    assert "task" in result.content
    assert result.content["task"]["is_completed"] is False


def test_delete_task_success():
    """Test successful delete_task operation."""
    tools = MCPTodoTools()

    # Create valid parameters
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    params = tools.DeleteTaskParams(
        user_id=user_id,
        task_id=task_id
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the todo service to return success
    with patch.object(tools.todo_service, 'delete_todo', return_value=True):
        result = tools.delete_task(params, mock_session)

    # Verify the result
    assert not result.is_error
    assert result.content["success"] is True
    assert result.content["message"] == "Task deleted successfully"


def test_delete_task_failure():
    """Test delete_task operation failure."""
    tools = MCPTodoTools()

    # Create valid parameters
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    params = tools.DeleteTaskParams(
        user_id=user_id,
        task_id=task_id
    )

    # Mock the database session
    mock_session = Mock(spec=Session)

    # Mock the todo service to return failure
    with patch.object(tools.todo_service, 'delete_todo', return_value=False):
        result = tools.delete_task(params, mock_session)

    # Verify the result
    assert result.is_error
    assert "error" in result.content
    assert "Failed to delete task" in result.content["error"]


def test_delete_task_invalid_uuids():
    """Test delete_task with invalid UUID formats."""
    tools = MCPTodoTools()

    # Create parameters with invalid UUID formats
    params = tools.DeleteTaskParams(
        user_id="invalid-uuid",
        task_id="invalid-task-id"
    )

    mock_session = Mock(spec=Session)
    result = tools.delete_task(params, mock_session)

    # Should return an error
    assert result.is_error
    assert "error" in result.content


if __name__ == "__main__":
    # Run the unit tests
    test_mcp_todo_tools_initialization()
    test_add_task_success()
    test_add_task_invalid_user_id()
    test_add_task_service_error()
    test_list_tasks_success()
    test_list_tasks_invalid_user_id()
    test_update_task_success()
    test_update_task_no_fields_provided()
    test_update_task_invalid_uuids()
    test_complete_task_success()
    test_complete_task_mark_incomplete()
    test_delete_task_success()
    test_delete_task_failure()
    test_delete_task_invalid_uuids()
    print("All unit tests passed!")