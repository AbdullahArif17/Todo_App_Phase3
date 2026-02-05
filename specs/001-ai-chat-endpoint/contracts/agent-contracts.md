# API Contracts: Todo Agent Integration

## Overview
This document defines the API contracts for integrating the Todo Agent with the chat endpoint system.

## Agent Configuration API

### Agent Initialization Contract

**Endpoint**: Internal (not exposed via HTTP)
**Method**: N/A (Initialization via OpenAI SDK)
**Description**: Initializes the Todo Agent with proper instructions and tools

**Input**:
```json
{
  "name": "Todo Assistant",
  "instructions": "You are a helpful todo management assistant that only uses MCP tools for all operations...",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "add_task",
        "description": "Add a new task for a user",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "string", "description": "The ID of the user creating the task"},
            "title": {"type": "string", "description": "The title of the task to create"},
            "description": {"type": "string", "description": "Optional description of the task"}
          },
          "required": ["user_id", "title"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_tasks",
        "description": "List tasks for a user",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "string", "description": "The ID of the user whose tasks to list"},
            "limit": {"type": "integer", "description": "Maximum number of tasks to return (default: 10)"},
            "offset": {"type": "integer", "description": "Number of tasks to skip (default: 0)"}
          },
          "required": ["user_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "update_task",
        "description": "Update an existing task for a user",
        "parameters": {
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
      }
    },
    {
      "type": "function",
      "function": {
        "name": "complete_task",
        "description": "Mark a task as complete or incomplete for a user",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "string", "description": "The ID of the task to update"},
            "is_completed": {"type": "boolean", "description": "Whether the task is completed (default: true)"}
          },
          "required": ["user_id", "task_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "delete_task",
        "description": "Delete a task for a user",
        "parameters": {
          "type": "object",
          "properties": {
            "user_id": {"type": "string", "description": "The ID of the user"},
            "task_id": {"type": "string", "description": "The ID of the task to delete"}
          },
          "required": ["user_id", "task_id"]
        }
      }
    }
  ],
  "model": "gpt-4-turbo"
}
```

## Chat Endpoint Integration Contract

### Request to Agent Contract

**Description**: How the chat service passes information to the agent

**Input to Agent**:
```json
{
  "thread_id": "thread_xxx",
  "messages": [
    {
      "role": "user",
      "content": "Add a task to buy groceries"
    }
  ],
  "user_context": {
    "user_id": "user_xxx",
    "conversation_id": "conv_xxx"
  }
}
```

### Agent Response Contract

**Description**: Expected structure of agent responses

**Output from Agent**:
```json
{
  "response_text": "I've added the task 'buy groceries' to your list.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {
        "user_id": "user_xxx",
        "title": "buy groceries"
      },
      "result": {
        "success": true,
        "task": {
          "id": "task_xxx",
          "title": "buy groceries",
          "is_completed": false
        }
      }
    }
  ],
  "action_metadata": {
    "operation": "add_task",
    "task_id": "task_xxx",
    "confirmation": "Task added successfully"
  }
}
```

## Tool Execution Contract

### Tool Call Execution Contract

**Description**: How the system executes MCP tools called by the agent

**Tool Call Input**:
```json
{
  "tool_name": "add_task",
  "arguments": {
    "user_id": "user_xxx",
    "title": "buy groceries",
    "description": "milk, bread, eggs"
  }
}
```

**Tool Call Output**:
```json
{
  "success": true,
  "result": {
    "success": true,
    "message": "Task 'buy groceries' added successfully",
    "task": {
      "id": "task_xxx",
      "title": "buy groceries",
      "description": "milk, bread, eggs",
      "is_completed": false
    }
  }
}
```

## Error Handling Contracts

### Tool Execution Error Contract

**Description**: How errors from MCP tools are handled and reported

**Error Output**:
```json
{
  "success": false,
  "result": {
    "success": false,
    "error": "Task not found or does not belong to user"
  }
}
```

### Agent Processing Error Contract

**Description**: How errors during agent processing are handled

**Error Response**:
```json
{
  "error": {
    "type": "agent_processing_error",
    "message": "The agent failed to process your request",
    "user_facing_message": "Sorry, I couldn't process your request. Please try again."
  }
}
```

## Integration Points

### With Chat Service

The agent integrates with the existing chat service through:

1. **Input**: Chat service passes user message and conversation context to agent
2. **Processing**: Agent uses MCP tools for all data operations
3. **Output**: Agent returns natural language response with action metadata
4. **Persistence**: Chat service saves both user message and agent response to database

### With MCP Server

The agent interacts with the MCP server through:

1. **Tool Registration**: MCP tools are registered with the agent at initialization
2. **Tool Execution**: Agent calls MCP tools when needed during processing
3. **Response Processing**: Tool responses are returned to agent for natural language processing
4. **Authentication**: User context is passed to MCP tools for authorization

## Performance Contracts

### Response Time SLA
- **P95**: Agent should respond within 3 seconds
- **P99**: Agent should respond within 5 seconds

### Availability SLA
- **Availability**: 99.9% uptime for agent functionality
- **Tool Availability**: MCP tools should be available 99.9% of the time

## Security Contracts

### Authentication
- User authentication must be validated before agent execution
- User context must be passed to all MCP tool calls
- Agent must respect user ownership of tasks

### Authorization
- Agent can only access tasks belonging to the authenticated user
- MCP tools must enforce user ownership validation
- Cross-user data access must be prevented