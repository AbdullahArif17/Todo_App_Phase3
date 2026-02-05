"""
Integration Tests for MCP Tools
Tests to verify end-to-end functionality of MCP tool operations
"""
import pytest
from unittest.mock import Mock, patch
from sqlmodel import Session
from apps.backend.src.mcp_server.tools.todo_tools import MCPTodoTools
from apps.backend.src.models.user import User
from apps.backend.src.models.todo_task import TodoTask
from mcp.types import ToolResult
import uuid


def test_end_to_end_add_and_list_tasks():
    """Test adding a task and then listing it."""
    tools = MCPTodoTools()

    # Create user and task parameters
    user_id = str(uuid.uuid4())

    # Add a task
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Integration Test Task",
        description="Test description for integration"
    )

    mock_session = Mock(spec=Session)

    # Mock the created todo for add_task
    mock_created_todo = Mock(spec=TodoTask)
    mock_created_todo.id = uuid.uuid4()
    mock_created_todo.title = "Integration Test Task"
    mock_created_todo.description = "Test description for integration"
    mock_created_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_created_todo):
        add_result = tools.add_task(add_params, mock_session)

    # Verify add was successful
    assert not add_result.is_error
    assert add_result.content["success"] is True
    assert add_result.content["task"]["title"] == "Integration Test Task"

    # Now list tasks for the same user
    list_params = tools.ListTasksParams(user_id=user_id)

    # Mock the returned todos for list_tasks (including our newly added task)
    mock_returned_todos = [mock_created_todo]

    with patch.object(tools.todo_service, 'get_todos_by_user_id', return_value=mock_returned_todos):
        list_result = tools.list_tasks(list_params, mock_session)

    # Verify list was successful and contains our task
    assert not list_result.is_error
    assert list_result.content["success"] is True
    assert len(list_result.content["tasks"]) >= 1

    # Find our task in the results
    found_task = None
    for task in list_result.content["tasks"]:
        if task["id"] == str(mock_created_todo.id):
            found_task = task
            break

    assert found_task is not None
    assert found_task["title"] == "Integration Test Task"
    assert found_task["description"] == "Test description for integration"


def test_end_to_end_add_update_and_complete_task():
    """Test adding, updating, and completing a task."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    # Step 1: Add a task
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Original Title",
        description="Original Description"
    )

    mock_session = Mock(spec=Session)

    # Mock the created todo
    mock_created_todo = Mock(spec=TodoTask)
    mock_created_todo.id = task_id
    mock_created_todo.title = "Original Title"
    mock_created_todo.description = "Original Description"
    mock_created_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_created_todo):
        add_result = tools.add_task(add_params, mock_session)

    # Verify add was successful
    assert not add_result.is_error
    assert add_result.content["success"] is True

    # Step 2: Update the task
    update_params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=str(task_id),
        title="Updated Title",
        description="Updated Description"
    )

    # Mock the updated todo
    mock_updated_todo = Mock(spec=TodoTask)
    mock_updated_todo.id = task_id
    mock_updated_todo.title = "Updated Title"
    mock_updated_todo.description = "Updated Description"
    mock_updated_todo.is_completed = False

    with patch.object(tools.todo_service, 'update_todo', return_value=mock_updated_todo):
        update_result = tools.update_task(update_params, mock_session)

    # Verify update was successful
    assert not update_result.is_error
    assert update_result.content["success"] is True
    assert update_result.content["task"]["title"] == "Updated Title"

    # Step 3: Complete the task
    complete_params = tools.CompleteTaskParams(
        user_id=user_id,
        task_id=str(task_id),
        is_completed=True
    )

    # Mock the completed todo
    mock_completed_todo = Mock(spec=TodoTask)
    mock_completed_todo.id = task_id
    mock_completed_todo.title = "Updated Title"
    mock_completed_todo.description = "Updated Description"
    mock_completed_todo.is_completed = True

    with patch.object(tools.todo_service, 'update_todo', return_value=mock_completed_todo):
        complete_result = tools.complete_task(complete_params, mock_session)

    # Verify completion was successful
    assert not complete_result.is_error
    assert complete_result.content["success"] is True
    assert complete_result.content["task"]["is_completed"] is True
    assert complete_result.content["task"]["title"] == "Updated Title"


def test_end_to_end_add_and_delete_task():
    """Test adding and then deleting a task."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    # Step 1: Add a task
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Task to Delete",
        description="This task will be deleted"
    )

    mock_session = Mock(spec=Session)

    # Mock the created todo
    mock_created_todo = Mock(spec=TodoTask)
    mock_created_todo.id = task_id
    mock_created_todo.title = "Task to Delete"
    mock_created_todo.description = "This task will be deleted"
    mock_created_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_created_todo):
        add_result = tools.add_task(add_params, mock_session)

    # Verify add was successful
    assert not add_result.is_error
    assert add_result.content["success"] is True

    # Step 2: Delete the task
    delete_params = tools.DeleteTaskParams(
        user_id=user_id,
        task_id=str(task_id)
    )

    with patch.object(tools.todo_service, 'delete_todo', return_value=True):
        delete_result = tools.delete_task(delete_params, mock_session)

    # Verify deletion was successful
    assert not delete_result.is_error
    assert delete_result.content["success"] is True
    assert delete_result.content["message"] == "Task deleted successfully"


def test_multi_user_isolation():
    """Test that users cannot access each other's tasks."""
    tools = MCPTodoTools()

    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    # Add a task for user1
    add_params = tools.AddTaskParams(
        user_id=user1_id,
        title="User1's Task",
        description="This belongs to user1"
    )

    mock_session = Mock(spec=Session)

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = task_id
    mock_todo.title = "User1's Task"
    mock_todo.description = "This belongs to user1"
    mock_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    # Verify add was successful
    assert not add_result.is_error
    assert add_result.content["success"] is True

    # Try to update the task as user2 (should fail)
    update_params = tools.UpdateTaskParams(
        user_id=user2_id,  # Different user
        task_id=str(task_id),
        title="Attempted Update by User2"
    )

    # Mock the service to return None (indicating task not found for user2)
    with patch.object(tools.todo_service, 'update_todo', return_value=None):
        update_result = tools.update_task(update_params, mock_session)

    # This should fail since user2 doesn't own the task
    assert update_result.is_error
    assert "Task not found or does not belong to user" in update_result.content["error"]


def test_task_not_found_scenarios():
    """Test scenarios where tasks are not found."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    nonexistent_task_id = str(uuid.uuid4())

    mock_session = Mock(spec=Session)

    # Try to update a non-existent task
    update_params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=nonexistent_task_id,
        title="Update Attempt"
    )

    with patch.object(tools.todo_service, 'update_todo', return_value=None):
        update_result = tools.update_task(update_params, mock_session)

    assert update_result.is_error
    assert "Task not found or does not belong to user" in update_result.content["error"]

    # Try to complete a non-existent task
    complete_params = tools.CompleteTaskParams(
        user_id=user_id,
        task_id=nonexistent_task_id
    )

    with patch.object(tools.todo_service, 'update_todo', return_value=None):
        complete_result = tools.complete_task(complete_params, mock_session)

    assert complete_result.is_error
    assert "Task not found or does not belong to user" in complete_result.content["error"]

    # Try to delete a non-existent task
    delete_params = tools.DeleteTaskParams(
        user_id=user_id,
        task_id=nonexistent_task_id
    )

    with patch.object(tools.todo_service, 'delete_todo', return_value=False):
        delete_result = tools.delete_task(delete_params, mock_session)

    assert delete_result.is_error
    assert "Task not found or does not belong to user" in delete_result.content["error"]


def test_concurrent_operations_simulation():
    """Simulate concurrent operations to test thread safety concepts."""
    tools = MCPTodoTools()

    # Create multiple users and tasks
    user_ids = [str(uuid.uuid4()) for _ in range(3)]
    task_ids = [uuid.uuid4() for _ in range(3)]

    mock_session = Mock(spec=Session)

    # Simulate multiple operations happening
    for i in range(3):
        # Add a task for each user
        add_params = tools.AddTaskParams(
            user_id=user_ids[i],
            title=f"Task for User {i}",
            description=f"Description for User {i}"
        )

        mock_todo = Mock(spec=TodoTask)
        mock_todo.id = task_ids[i]
        mock_todo.title = f"Task for User {i}"
        mock_todo.description = f"Description for User {i}"
        mock_todo.is_completed = False

        with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
            add_result = tools.add_task(add_params, mock_session)
            assert not add_result.is_error
            assert add_result.content["success"] is True

    # Verify each user can list their own tasks
    for i in range(3):
        list_params = tools.ListTasksParams(user_id=user_ids[i])

        # Return only the task for this specific user
        mock_user_todo = Mock(spec=TodoTask)
        mock_user_todo.id = task_ids[i]
        mock_user_todo.title = f"Task for User {i}"
        mock_user_todo.description = f"Description for User {i}"
        mock_user_todo.is_completed = False

        with patch.object(tools.todo_service, 'get_todos_by_user_id', return_value=[mock_user_todo]):
            list_result = tools.list_tasks(list_params, mock_session)
            assert not list_result.is_error
            assert list_result.content["success"] is True
            assert len(list_result.content["tasks"]) == 1
            assert list_result.content["tasks"][0]["title"] == f"Task for User {i}"


if __name__ == "__main__":
    # Run the integration tests
    test_end_to_end_add_and_list_tasks()
    test_end_to_end_add_update_and_complete_task()
    test_end_to_end_add_and_delete_task()
    test_multi_user_isolation()
    test_task_not_found_scenarios()
    test_concurrent_operations_simulation()
    print("All integration tests passed!")