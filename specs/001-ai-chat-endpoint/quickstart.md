# Quickstart: Todo Agent Implementation

## Overview
This guide covers setting up and running the Todo Agent that uses OpenAI Agents SDK to interact with todo operations via MCP tools.

## Prerequisites
- Python 3.11+
- OpenAI API key
- MCP Server running with todo tools available
- PostgreSQL database configured

## Environment Setup

### 1. Install Dependencies
```bash
pip install openai
```

### 2. Configure Environment Variables
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_ORGANIZATION="your-org-id"  # if applicable
```

## Agent Configuration

### 1. Define Agent Instructions
The agent should be configured with instructions that guide it to:
- Only use MCP tools for all todo operations
- Ask for clarification when task identity is ambiguous
- Confirm successful actions in natural language
- Handle errors gracefully and explain them to users

### 2. Register MCP Tools
The agent must have access to these MCP tools:
- `add_task`: Add a new task for a user
- `list_tasks`: List tasks for a user
- `update_task`: Update an existing task for a user
- `complete_task`: Mark a task as complete or incomplete
- `delete_task`: Delete a task for a user

## Basic Usage

### 1. Initialize the Agent
```python
from openai import OpenAI
client = OpenAI()

agent = client.beta.agents.create(
    name="Todo Assistant",
    instructions="You are a helpful todo management assistant...",
    tools=[...],  # MCP tools definitions
    model="gpt-4-turbo"
)
```

### 2. Create a Thread for Conversation
```python
thread = client.beta.threads.create()
```

### 3. Add User Message
```python
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Add a task to buy groceries"
)
```

### 4. Run the Agent
```python
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    agent_id=agent.id
)
```

### 5. Process Tool Calls
The agent will call MCP tools as needed. You'll need to implement a run loop that:
- Checks if the run requires action (tool calls)
- Executes the requested MCP tools
- Submits the tool outputs back to the agent
- Waits for the run to complete

## Integration with Chat Endpoint

The Todo Agent integrates with the existing `/api/{user_id}/chat` endpoint:

1. User sends a message to the chat endpoint
2. The system retrieves conversation history from the database
3. The agent is invoked with the user's message and conversation context
4. The agent processes the request using MCP tools as needed
5. The agent's response is saved to the database
6. The response is returned to the user

## Running the System

### 1. Start the MCP Server
Make sure the MCP server with todo tools is running before starting the main application.

### 2. Start the Backend API
```bash
cd apps/backend
uvicorn src.api.main:app --reload
```

### 3. Send Requests to the Chat Endpoint
```bash
curl -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Authorization: Bearer {auth_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy milk"}'
```

## Development Workflow

### Local Development
1. Set up virtual environment: `python -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Run tests: `pytest tests/test_agents/`
5. Start development server: `uvicorn src.api.main:app --reload`

### Testing the Agent
- Unit tests: `pytest tests/test_agents/test_todo_agent.py`
- Integration tests: `pytest tests/integration/test_agent_integration.py`
- End-to-end tests: `pytest tests/test_api/test_chat.py`

## Troubleshooting

### Agent Not Calling Tools
- Verify MCP tools are properly registered with the agent
- Check that tool schemas match the expected parameters
- Ensure the agent's instructions clearly indicate when to use tools

### Authentication Issues
- Verify that user authentication is working properly
- Check that user_id is correctly passed to the agent context
- Ensure the agent respects user ownership of tasks

### Performance Issues
- Monitor tool call response times
- Check for unnecessary tool chaining
- Verify database connection pooling is configured properly