"""
Performance and Load Tests for MCP Server
Tests to verify MCP tools performance under various loads
"""
import time
import asyncio
import pytest
from unittest.mock import Mock
from sqlmodel import Session
from mcp_server.tools.todo_tools import MCPTodoTools
from models.todo_task import TodoTask
import uuid


def test_single_operation_performance():
    """Test performance of individual operations."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    mock_session = Mock(spec=Session)

    # Mock the todo objects
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = task_id
    mock_todo.title = "Performance Test Task"
    mock_todo.description = "Task for performance testing"
    mock_todo.is_completed = False

    # Test add_task performance
    start_time = time.time()

    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Performance Test Task",
        description="Task for performance testing"
    )

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        add_result = tools.add_task(add_params, mock_session)

    add_duration = time.time() - start_time

    # Verify the operation succeeded
    assert not add_result.is_error
    assert add_result.content["success"] is True

    # Check that the operation completed within acceptable time (under 1 second)
    assert add_duration < 1.0, f"add_task took {add_duration:.3f}s, expected < 1.0s"

    # Test list_tasks performance
    start_time = time.time()

    list_params = tools.ListTasksParams(user_id=user_id)

    with patch.object(tools.todo_service, 'get_todos_by_user_id', return_value=[mock_todo]):
        list_result = tools.list_tasks(list_params, mock_session)

    list_duration = time.time() - start_time

    # Verify the operation succeeded
    assert not list_result.is_error
    assert list_result.content["success"] is True

    # Check that the operation completed within acceptable time
    assert list_duration < 1.0, f"list_tasks took {list_duration:.3f}s, expected < 1.0s"

    # Test update_task performance
    start_time = time.time()

    update_params = tools.UpdateTaskParams(
        user_id=user_id,
        task_id=str(task_id),
        title="Updated Performance Test Task"
    )

    mock_updated_todo = Mock(spec=TodoTask)
    mock_updated_todo.id = task_id
    mock_updated_todo.title = "Updated Performance Test Task"
    mock_updated_todo.description = "Task for performance testing"
    mock_updated_todo.is_completed = False

    with patch.object(tools.todo_service, 'update_todo', return_value=mock_updated_todo):
        update_result = tools.update_task(update_params, mock_session)

    update_duration = time.time() - start_time

    # Verify the operation succeeded
    assert not update_result.is_error
    assert update_result.content["success"] is True

    # Check that the operation completed within acceptable time
    assert update_duration < 1.0, f"update_task took {update_duration:.3f}s, expected < 1.0s"


def test_concurrent_operations_performance():
    """Test performance under concurrent operations."""
    import threading
    import queue

    tools = MCPTodoTools()
    results_queue = queue.Queue()

    def perform_operation(op_id):
        """Perform a single operation in a thread."""
        try:
            user_id = str(uuid.uuid4())
            task_id = str(uuid.uuid4())

            mock_session = Mock(spec=Session)

            # Mock the todo objects
            mock_todo = Mock(spec=TodoTask)
            mock_todo.id = task_id
            mock_todo.title = f"Concurrent Task {op_id}"
            mock_todo.description = f"Task {op_id} for concurrent testing"
            mock_todo.is_completed = False

            # Perform add_task
            add_params = tools.AddTaskParams(
                user_id=user_id,
                title=f"Concurrent Task {op_id}",
                description=f"Task {op_id} for concurrent testing"
            )

            with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
                result = tools.add_task(add_params, mock_session)

            results_queue.put(("success", op_id, result))
        except Exception as e:
            results_queue.put(("error", op_id, str(e)))

    # Start multiple threads to perform operations concurrently
    num_threads = 10
    threads = []

    start_time = time.time()

    for i in range(num_threads):
        thread = threading.Thread(target=perform_operation, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    total_duration = time.time() - start_time

    # Check results
    successes = 0
    errors = 0

    while not results_queue.empty():
        result_type, op_id, result = results_queue.get()
        if result_type == "success":
            successes += 1
            assert not result.is_error
            assert result.content["success"] is True
        else:
            errors += 1

    # Verify that all operations succeeded
    assert successes == num_threads, f"Expected {num_threads} successes, got {successes}"
    assert errors == 0, f"Got {errors} errors in concurrent operations"

    # Check that all operations completed within reasonable time
    # For 10 concurrent operations, allow up to 3 seconds total
    assert total_duration < 3.0, f"All concurrent operations took {total_duration:.3f}s, expected < 3.0s"

    # Calculate average time per operation
    avg_duration = total_duration / num_threads
    assert avg_duration < 1.0, f"Average operation time was {avg_duration:.3f}s, expected < 1.0s"


def test_large_payload_handling():
    """Test handling of larger payloads."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())

    # Create a large description to test payload handling
    large_description = "This is a large description. " * 100  # 2000+ characters

    mock_session = Mock(spec=Session)

    # Mock the todo object
    mock_todo = Mock(spec=TodoTask)
    mock_todo.id = uuid.uuid4()
    mock_todo.title = "Large Payload Test Task"
    mock_todo.description = large_description
    mock_todo.is_completed = False

    start_time = time.time()

    add_params = tools.AddTaskParams(
        user_id=user_id,
        title="Large Payload Test Task",
        description=large_description
    )

    with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
        result = tools.add_task(add_params, mock_session)

    duration = time.time() - start_time

    # Verify the operation succeeded despite large payload
    assert not result.is_error
    assert result.content["success"] is True
    assert "Large Payload Test Task" in result.content["message"]

    # Check that it completed in reasonable time
    assert duration < 2.0, f"Large payload operation took {duration:.3f}s, expected < 2.0s"


def test_multiple_users_performance():
    """Test performance with multiple different users."""
    tools = MCPTodoTools()

    num_users = 20
    user_ids = [str(uuid.uuid4()) for _ in range(num_users)]
    results = []

    start_time = time.time()

    for i, user_id in enumerate(user_ids):
        mock_session = Mock(spec=Session)

        # Mock the todo object for this user
        mock_todo = Mock(spec=TodoTask)
        mock_todo.id = uuid.uuid4()
        mock_todo.title = f"User {i} Task"
        mock_todo.description = f"Task for user {i}"
        mock_todo.is_completed = False

        # Add a task for each user
        add_params = tools.AddTaskParams(
            user_id=user_id,
            title=f"User {i} Task",
            description=f"Task for user {i}"
        )

        with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
            result = tools.add_task(add_params, mock_session)

        results.append((user_id, result))

    total_duration = time.time() - start_time

    # Verify all operations succeeded
    for user_id, result in results:
        assert not result.is_error
        assert result.content["success"] is True

    # Check that all operations completed within reasonable time
    assert total_duration < 5.0, f"Operations for {num_users} users took {total_duration:.3f}s, expected < 5.0s"

    # Calculate average time per user operation
    avg_duration = total_duration / num_users
    assert avg_duration < 0.5, f"Average per-user operation time was {avg_duration:.3f}s, expected < 0.5s"


def test_repeated_operations_performance():
    """Test performance of repeated operations by the same user."""
    tools = MCPTodoTools()

    user_id = str(uuid.uuid4())
    mock_session = Mock(spec=Session)

    num_operations = 15

    # Mock different todo objects for each operation
    start_time = time.time()

    for i in range(num_operations):
        mock_todo = Mock(spec=TodoTask)
        mock_todo.id = uuid.uuid4()
        mock_todo.title = f"Repeated Task {i}"
        mock_todo.description = f"Task {i} for repeated operations test"
        mock_todo.is_completed = False

        # Add a task
        add_params = tools.AddTaskParams(
            user_id=user_id,
            title=f"Repeated Task {i}",
            description=f"Task {i} for repeated operations test"
        )

        with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
            result = tools.add_task(add_params, mock_session)

        assert not result.is_error
        assert result.content["success"] is True

    total_duration = time.time() - start_time

    # Check that all operations completed within reasonable time
    assert total_duration < 5.0, f"{num_operations} repeated operations took {total_duration:.3f}s, expected < 5.0s"

    # Calculate average time per operation
    avg_duration = total_duration / num_operations
    assert avg_duration < 0.5, f"Average repeated operation time was {avg_duration:.3f}s, expected < 0.5s"


def test_memory_usage_stability():
    """Test that memory usage remains stable during operations."""
    import gc
    import psutil
    import os

    tools = MCPTodoTools()

    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Perform multiple operations
    num_operations = 50

    for i in range(num_operations):
        user_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())

        mock_session = Mock(spec=Session)

        mock_todo = Mock(spec=TodoTask)
        mock_todo.id = task_id
        mock_todo.title = f"Memory Test Task {i}"
        mock_todo.description = f"Task {i} for memory usage test"
        mock_todo.is_completed = False

        add_params = tools.AddTaskParams(
            user_id=user_id,
            title=f"Memory Test Task {i}",
            description=f"Task {i} for memory usage test"
        )

        with patch.object(tools.todo_service, 'create_todo', return_value=mock_todo):
            result = tools.add_task(add_params, mock_session)

        assert not result.is_error

        # Force garbage collection periodically
        if i % 10 == 0:
            gc.collect()

    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Memory increase should be reasonable (less than 50MB for 50 operations)
    memory_increase = final_memory - initial_memory
    assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB after {num_operations} operations, expected < 50MB"


if __name__ == "__main__":
    from unittest.mock import patch
    # Run the performance tests
    test_single_operation_performance()
    test_concurrent_operations_performance()
    test_large_payload_handling()
    test_multiple_users_performance()
    test_repeated_operations_performance()
    test_memory_usage_stability()
    print("All performance tests passed!")