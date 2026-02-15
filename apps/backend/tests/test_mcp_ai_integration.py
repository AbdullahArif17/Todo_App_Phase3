"""
AI Agent Integration Tests for MCP Server
Tests to verify MCP tools work properly with AI agents
"""
import pytest
from unittest.mock import Mock, patch
from sqlmodel import Session
from mcp_server.tools.todo_tools import MCPTodoTools
from mcp_server.main import mcp_todo_server
from models.user import User
from models.todo_task import TodoTask
from mcp.types import ToolResult
import uuid


def test_mcp_server_tool_availability():
    """Test that all required MCP tools are available in the server."""
    server = mcp_todo_server.get_server()

    # Check that all required tools are registered
    required_tools = ['add_task', 'list_tasks', 'update_task', 'complete_task', 'delete_task']

    for tool_name in required_tools:
        assert tool_name in server._tools, f"Tool {tool_name} not found in server"

    # Verify each tool has proper properties
    for tool_name in required_tools:
        tool = server._tools[tool_name]
        assert tool.name == tool_name
        assert hasattr(tool, 'input_schema')
        assert isinstance(tool.input_schema, dict)


def test_ai_agent_scenario_simple_task_management():
    """Test a simple task management scenario as an AI agent would use it."""
    tools = MCPTodoTools()

    # Simulate an AI agent interaction: User wants to add a task
    user_id = str(uuid.uuid4())

    # AI agent processes: "Add a task to buy milk"
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Buy milk",
        description="Get 2% milk from the grocery store"
    )

    mock_session = Mock(spec=Session)

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = uuid.uuid4()
    mock_todo.title = "Buy milk"
    mock_todo.description = "Get 2% milk from the grocery store"
    mock_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    assert not add_result.is_error
    assert add_result.content["success"] is True
    assert "Buy milk" in add_result.content["message"]

    # AI agent processes: "What tasks do I have?"
    list_params = tools.ListTasksParams(user_id=user_id)

    # Mock returning the task we just created
    with patch.object(tools.todo_service, 'get_todos_by_user_id', return_value=[mock_todo]):
        list_result = tools.list_tasks(list_params, mock_session)

    assert not list_result.is_error
    assert list_result.content["success"] is True
    assert len(list_result.content["tasks"]) == 1
    assert list_result.content["tasks"][0]["title"] == "Buy milk"


def test_ai_agent_scenario_task_completion_workflow():
    """Test a task completion workflow as an AI agent would use it."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    mock_session = Mock(spec=Session)

    # First, add a task
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Review quarterly report",
        description="Review and provide feedback on Q4 report"
    )

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = task_id
    mock_todo.title = "Review quarterly report"
    mock_todo.description = "Review and provide feedback on Q4 report"
    mock_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    assert not add_result.is_error
    assert add_result.content["success"] is True

    # AI agent now wants to complete the task: "Mark the quarterly report as complete"
    complete_params = tools.CompleteTaskParams(
        user_id=user_id,
        task_id=str(task_id),
        is_completed=True
    )

    # Mock the completed todo
    mock_completed_todo = Mock(spec=TodoTask)
    mock_completed_todo.id = task_id
    mock_completed_todo.title = "Review quarterly report"
    mock_completed_todo.description = "Review and provide feedback on Q4 report"
    mock_completed_todo.is_completed = True

    with patch.object(tools.todo_service, 'update_todo', return_value=mock_completed_todo):
        complete_result = tools.complete_task(complete_params, mock_session)

    assert not complete_result.is_error
    assert complete_result.content["success"] is True
    assert "completed" in complete_result.content["message"]


def test_ai_agent_scenario_task_update_workflow():
    """Test a task update workflow as an AI agent would use it."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    mock_session = Mock(spec=Session)

    # First, add a task
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Team meeting",
        description="Weekly team sync"
    )

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = task_id
    mock_todo.title = "Team meeting"
    mock_todo.description = "Weekly team sync"
    mock_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    assert not add_result.is_error
    assert add_result.content["success"] is True

    # AI agent now wants to update the task: "Change the team meeting description to include agenda items"
    update_params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=str(task_id),
        description="Weekly team sync with agenda items and action items"
    )

    # Mock the updated todo
    mock_updated_todo = Mock(spec=TodoTask)
    mock_updated_todo.id = task_id
    mock_updated_todo.title = "Team meeting"
    mock_updated_todo.description = "Weekly team sync with agenda items and action items"
    mock_updated_todo.is_completed = False

    with patch.object(tools.todo_service, 'update_todo', return_value=mock_updated_todo):
        update_result = tools.update_task(update_params, mock_session)

    assert not update_result.is_error
    assert update_result.content["success"] is True
    assert update_result.content["task"]["description"] == "Weekly team sync with agenda items and action items"


def test_ai_agent_scenario_task_deletion_workflow():
    """Test a task deletion workflow as an AI agent would use it."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    mock_session = Mock(spec=Session)

    # First, add a task
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Old task to delete",
        description="This task is no longer needed"
    )

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = task_id
    mock_todo.title = "Old task to delete"
    mock_todo.description = "This task is no longer needed"
    mock_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    assert not add_result.is_error
    assert add_result.content["success"] is True

    # AI agent now wants to delete the task: "Remove the old task"
    delete_params = tools.DeleteTaskParams(
        user_id=user_id,
        task_id=str(task_id)
    )

    with patch.object(tools.todo_service, 'delete_todo', return_value=True):
        delete_result = tools.delete_task(delete_params, mock_session)

    assert not delete_result.is_error
    assert delete_result.content["success"] is True
    assert delete_result.content["message"] == "Task deleted successfully"


def test_ai_agent_error_handling():
    """Test how MCP tools handle errors that an AI agent might encounter."""
    tools = MCPTodoTools()

    # Test invalid user_id format
    invalid_params = tools.AddTaskParams(
        user_id="not-a-uuid",
        title="Test task"
    )

    mock_session = Mock(spec=Session)
    result = tools.add_task(invalid_params, mock_session)

    assert result.is_error
    assert "error" in result.content
    assert "Invalid UUID format" in result.content["error"]

    # Test operation on non-existent task
    user_id = str(uuid.uuid4())
    nonexistent_task_id = str(uuid.uuid4())

    update_params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=nonexistent_task_id,
        title="Updated title"
    )

    with patch.object(tools.todo_service, 'update_todo', return_value=None):
        update_result = tools.update_task(update_params, mock_session)

    assert update_result.is_error
    assert "Task not found or does not belong to user" in update_result.content["error"]


def test_ai_agent_response_format_compatibility():
    """Test that MCP tool responses are compatible with AI agent expectations."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = uuid.uuid4()

    mock_session = Mock(spec=Session)

    # Test add_task response format
    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="AI Compatible Task",
        description="Task created for AI agent testing"
    )

    # Mock the created todo
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = task_id
    mock_todo.title = "AI Compatible Task"
    mock_todo.description = "Task created for AI agent testing"
    mock_todo.is_completed = False

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    # Verify response structure is AI-friendly
    assert hasattr(add_result, 'content')
    assert 'success' in add_result.content
    assert 'message' in add_result.content
    assert 'task' in add_result.content
    assert isinstance(add_result.content['task'], dict)
    assert 'id' in add_result.content['task']
    assert 'title' in add_result.content['task']

    # Test list_tasks response format
    list_params = tools.ListTasksParams(user_id=user_id)

    with patch.object(tools.todo_service, 'get_todos_by_user_id', return_value=[mock_todo]):
        list_result = tools.list_tasks(list_params, mock_session)

    # Verify list response structure is AI-friendly
    assert hasattr(list_result, 'content')
    assert 'success' in list_result.content
    assert 'tasks' in list_result.content
    assert isinstance(list_result.content['tasks'], list)
    if list_result.content['tasks']:
        task = list_result.content['tasks'][0]
        assert 'id' in task
        assert 'title' in task
        assert 'is_completed' in task


def test_mcp_server_tool_execution():
    """Test that tools can be executed as expected by an AI agent framework."""
    # Get the server instance
    server = mcp_todo_server.get_server()

    # Verify that the server has the expected tools
    assert hasattr(server, '_tools')
    assert len(server._tools) >= 5  # We have 5 required tools

    # Test that each tool has an executable function
    for tool_name, tool_obj in server._tools.items():
        assert hasattr(tool_obj, 'fn') or hasattr(tool_obj, '_handler')


if __name__ == "__main__":
    # Run the AI integration tests
    test_mcp_server_tool_availability()
    test_ai_agent_scenario_simple_task_management()
    test_ai_agent_scenario_task_completion_workflow()
    test_ai_agent_scenario_task_update_workflow()
    test_ai_agent_scenario_task_deletion_workflow()
    test_ai_agent_error_handling()
    test_ai_agent_response_format_compatibility()
    test_mcp_server_tool_execution()
    print("All AI integration tests passed!")