"""
Tool Registration Tests for MCP Server
Tests to verify proper registration and functionality of MCP tools
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp.types import ToolResult
import uuid

from apps.backend.src.mcp_server.tools.todo_tools import MCPTodoTools, AddTaskParams, ListTasksParams, UpdateTaskParams, CompleteTaskParams, DeleteTaskParams
from apps.backend.src.mcp_server.main import mcp_todo_server


def test_add_task_tool_registered():
    """Test that add_task tool is properly registered with the MCP server."""
    server = mcp_todo_server.get_server()

    # Check that the tool exists in the server's registry
    assert hasattr(server, '_tools')
    assert 'add_task' in server._tools

    # Check tool properties
    tool = server._tools['add_task']
    assert tool.name == 'add_task'
    assert 'user_id' in tool.input_schema['properties']
    assert 'title' in tool.input_schema['properties']


def test_list_tasks_tool_registered():
    """Test that list_tasks tool is properly registered with the MCP server."""
    server = mcp_todo_server.get_server()

    # Check that the tool exists in the server's registry
    assert 'list_tasks' in server._tools

    # Check tool properties
    tool = server._tools['list_tasks']
    assert tool.name == 'list_tasks'
    assert 'user_id' in tool.input_schema['properties']


def test_update_task_tool_registered():
    """Test that update_task tool is properly registered with the MCP server."""
    server = mcp_todo_server.get_server()

    # Check that the tool exists in the server's registry
    assert 'update_task' in server._tools

    # Check tool properties
    tool = server._tools['update_task']
    assert tool.name == 'update_task'
    assert 'user_id' in tool.input_schema['properties']
    assert 'task_id' in tool.input_schema['properties']


def test_complete_task_tool_registered():
    """Test that complete_task tool is properly registered with the MCP server."""
    server = mcp_todo_server.get_server()

    # Check that the tool exists in the server's registry
    assert 'complete_task' in server._tools

    # Check tool properties
    tool = server._tools['complete_task']
    assert tool.name == 'complete_task'
    assert 'user_id' in tool.input_schema['properties']
    assert 'task_id' in tool.input_schema['properties']


def test_delete_task_tool_registered():
    """Test that delete_task tool is properly registered with the MCP server."""
    server = mcp_todo_server.get_server()

    # Check that the tool exists in the server's registry
    assert 'delete_task' in server._tools

    # Check tool properties
    tool = server._tools['delete_task']
    assert tool.name == 'delete_task'
    assert 'user_id' in tool.input_schema['properties']
    assert 'task_id' in tool.input_schema['properties']


def test_tool_descriptions():
    """Test that all tools have appropriate descriptions."""
    server = mcp_todo_server.get_server()

    # Check descriptions for all tools
    assert server._tools['add_task'].description.startswith("Add a new task")
    assert server._tools['list_tasks'].description.startswith("List tasks")
    assert server._tools['update_task'].description.startswith("Update an existing task")
    assert server._tools['complete_task'].description.startswith("Mark a task as complete")
    assert server._tools['delete_task'].description.startswith("Delete a task")


def test_todo_tools_initialization():
    """Test that MCPTodoTools initializes correctly."""
    tools = MCPTodoTools()
    assert tools.todo_service is not None


def test_add_task_params_validation():
    """Test validation of AddTaskParams."""
    user_id = str(uuid.uuid4())

    # Valid parameters
    params = AddTaskParams(user_id=user_id, title="Test Task")
    assert params.user_id == user_id
    assert params.title == "Test Task"

    # Valid with description
    params_with_desc = AddTaskParams(user_id=user_id, title="Test Task", description="Test Description")
    assert params_with_desc.user_id == user_id
    assert params_with_desc.title == "Test Task"
    assert params_with_desc.description == "Test Description"

    # Test with empty description (should default to "")
    params_empty_desc = AddTaskParams(user_id=user_id, title="Test Task", description="")
    assert params_empty_desc.description == ""


def test_list_tasks_params_validation():
    """Test validation of ListTasksParams."""
    user_id = str(uuid.uuid4())

    # Valid parameters
    params = ListTasksParams(user_id=user_id)
    assert params.user_id == user_id
    assert params.limit == 10
    assert params.offset == 0

    # Valid with custom limit and offset
    params_custom = ListTasksParams(user_id=user_id, limit=5, offset=2)
    assert params_custom.user_id == user_id
    assert params_custom.limit == 5
    assert params_custom.offset == 2


def test_update_task_params_validation():
    """Test validation of UpdateTaskParams."""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # Valid parameters with all fields
    params = UpdateTaskParams(
        user_id=user_id,
        task_id=task_id,
        title="Updated Title",
        description="Updated Description",
        is_completed=True
    )
    assert params.user_id == user_id
    assert params.task_id == task_id
    assert params.title == "Updated Title"
    assert params.description == "Updated Description"
    assert params.is_completed is True

    # Valid with only required fields
    params_required = UpdateTaskParams(user_id=user_id, task_id=task_id)
    assert params_required.user_id == user_id
    assert params_required.task_id == task_id
    assert params_required.title is None
    assert params_required.description is None
    assert params_required.is_completed is None


def test_complete_task_params_validation():
    """Test validation of CompleteTaskParams."""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # Valid parameters with default completion status
    params_default = CompleteTaskParams(user_id=user_id, task_id=task_id)
    assert params_default.user_id == user_id
    assert params_default.task_id == task_id
    assert params_default.is_completed is True  # Default value

    # Valid parameters with explicit completion status
    params_explicit = CompleteTaskParams(user_id=user_id, task_id=task_id, is_completed=False)
    assert params_explicit.is_completed is False


def test_delete_task_params_validation():
    """Test validation of DeleteTaskParams."""
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # Valid parameters
    params = DeleteTaskParams(user_id=user_id, task_id=task_id)
    assert params.user_id == user_id
    assert params.task_id == task_id


if __name__ == "__main__":
    # Run the tests
    test_add_task_tool_registered()
    test_list_tasks_tool_registered()
    test_update_task_tool_registered()
    test_complete_task_tool_registered()
    test_delete_task_tool_registered()
    test_tool_descriptions()
    test_todo_tools_initialization()
    test_add_task_params_validation()
    test_list_tasks_params_validation()
    test_update_task_params_validation()
    test_complete_task_params_validation()
    test_delete_task_params_validation()
    print("All registration tests passed!")