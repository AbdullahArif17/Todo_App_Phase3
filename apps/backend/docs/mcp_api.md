# MCP Server API Documentation

## Overview
The MCP (Model Context Protocol) Server exposes todo operations as standardized tools for AI agents. The server uses the Official MCP SDK to provide a consistent interface for managing todo tasks through natural language interactions.

## Available Tools

### add_task
Adds a new task for a user.

**Parameters:**
- `user_id` (string, required): The ID of the user creating the task
- `title` (string, required): The title of the task to create
- `description` (string, optional): Optional description of the task

**Example Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_task",
    "arguments": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, bread, eggs"
    }
  }
}
```

**Example Response:**
```json
{
  "result": {
    "success": true,
    "message": "Task 'Buy groceries' added successfully",
    "task": {
      "id": "987e6543-e21b-32d1-a654-426614174999",
      "title": "Buy groceries",
      "description": "Milk, bread, eggs",
      "is_completed": false
    }
  }
}
```

### list_tasks
Lists tasks for a user.

**Parameters:**
- `user_id` (string, required): The ID of the user whose tasks to list
- `limit` (integer, optional): Maximum number of tasks to return (default: 10)
- `offset` (integer, optional): Number of tasks to skip (default: 0)

**Example Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "list_tasks",
    "arguments": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "limit": 5,
      "offset": 0
    }
  }
}
```

**Example Response:**
```json
{
  "result": {
    "success": true,
    "message": "Retrieved 2 tasks for user",
    "tasks": [
      {
        "id": "987e6543-e21b-32d1-a654-426614174999",
        "title": "Buy groceries",
        "description": "Milk, bread, eggs",
        "is_completed": false
      },
      {
        "id": "876e5432-d10a-21c0-z345-315503063888",
        "title": "Walk the dog",
        "description": "",
        "is_completed": true
      }
    ]
  }
}
```

### update_task
Updates an existing task for a user.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `task_id` (string, required): The ID of the task to update
- `title` (string, optional): New title for the task
- `description` (string, optional): New description for the task
- `is_completed` (boolean, optional): New completion status for the task

**Example Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "update_task",
    "arguments": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_id": "987e6543-e21b-32d1-a654-426614174999",
      "title": "Buy groceries and cook dinner"
    }
  }
}
```

**Example Response:**
```json
{
  "result": {
    "success": true,
    "message": "Task 'Buy groceries and cook dinner' updated successfully",
    "task": {
      "id": "987e6543-e21b-32d1-a654-426614174999",
      "title": "Buy groceries and cook dinner",
      "description": "Milk, bread, eggs",
      "is_completed": false
    }
  }
}
```

### complete_task
Marks a task as complete or incomplete for a user.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `task_id` (string, required): The ID of the task to update
- `is_completed` (boolean, optional): Whether the task is completed (default: true)

**Example Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "complete_task",
    "arguments": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_id": "987e6543-e21b-32d1-a654-426614174999",
      "is_completed": true
    }
  }
}
```

**Example Response:**
```json
{
  "result": {
    "success": true,
    "message": "Task 'Buy groceries and cook dinner' has been completed",
    "task": {
      "id": "987e6543-e21b-32d1-a654-426614174999",
      "title": "Buy groceries and cook dinner",
      "description": "Milk, bread, eggs",
      "is_completed": true
    }
  }
}
```

### delete_task
Deletes a task for a user.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `task_id` (string, required): The ID of the task to delete

**Example Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "delete_task",
    "arguments": {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "task_id": "987e6543-e21b-32d1-a654-426614174999"
    }
  }
}
```

**Example Response:**
```json
{
  "result": {
    "success": true,
    "message": "Task deleted successfully"
  }
}
```

## Error Responses

When an operation fails, the MCP server returns a structured error response:

```json
{
  "result": {
    "success": false,
    "error": "Detailed error message explaining what went wrong"
  }
}
```

### Common Error Types
- `Invalid UUID format for user_id`: Returned when the user_id parameter is not a valid UUID
- `Task not found or does not belong to user`: Returned when trying to access a task that doesn't exist or belongs to another user
- `No fields provided for update`: Returned by update_task when no update parameters are provided
- `Failed to delete task`: Returned when the delete operation fails

## Security Considerations

- All operations require a valid user_id parameter that must match the authenticated user context
- Users can only access, modify, or delete tasks that belong to them
- All inputs are validated and sanitized before processing
- Access attempts to other users' tasks are logged for security monitoring

## Rate Limiting

The MCP server implements rate limiting to prevent abuse:
- Default limit: 30 requests per minute per user
- Exceeding the limit results in temporary blocking
- Rate limit events are logged for monitoring

## Monitoring

All MCP tool access is logged for:
- Security monitoring
- Usage analytics
- Debugging and troubleshooting