# Quickstart Guide: Stateless Chat Architecture with AI Agent

## Overview
This guide helps you set up and run the stateless chat architecture with AI agent integration for todo management. The system provides a REST API endpoint that processes natural language messages through an AI agent using MCP tools for todo operations.

## Prerequisites
- Python 3.11+
- PostgreSQL database (or Neon Serverless PostgreSQL)
- OpenAI API key
- Node.js 18+ (for frontend, if applicable)

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
NEON_DATABASE_URL=your_neon_connection_string

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo  # or gpt-4o-mini for cost efficiency

# Application Settings
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8000
ENVIRONMENT=development
DEBUG=true
```

## Database Setup

### 1. Run Database Migrations
```bash
# If using alembic for migrations
alembic upgrade head

# Or run the initialization script
python -m apps.backend.src.database.initialize
```

### 2. Verify Database Connection
```bash
python -c "from apps.backend.src.database import engine; print('Database connection successful')"
```

## Running the Application

### 1. Start the Backend Server
```bash
# Using uvicorn
uvicorn apps.backend.src.main:app --host 0.0.0.0 --port 8000 --reload

# Or using the run script if available
python -m apps.backend.src.run
```

### 2. Verify the Chat Endpoint
Once the server is running, the chat endpoint will be available at:
- POST `/api/{user_id}/chat`

## Testing the API

### 1. Using curl
```bash
# First, you'll need to obtain an authentication token
# Then make a request to the chat endpoint:

curl -X POST "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'
```

### 2. Using Python requests
```python
import requests
import uuid

user_id = str(uuid.uuid4())  # Or use an existing user ID
headers = {
    "Authorization": "Bearer YOUR_AUTH_TOKEN",
    "Content-Type": "application/json"
}

# Create a new conversation
payload = {
    "message": "Add a task to buy groceries",
    "conversation_id": None  # Will create a new conversation
}

response = requests.post(
    f"http://localhost:8000/api/{user_id}/chat",
    json=payload,
    headers=headers
)

print(response.json())
```

## Key Components

### 1. Todo Agent
The AI agent that processes natural language and uses MCP tools for todo operations:
- Located at: `apps/backend/src/agents/todo_agent.py`
- Uses OpenAI Agents SDK for tool calling
- Interprets user intent and selects appropriate tools

### 2. MCP Tools
Standardized tools for todo operations:
- `add_task`: Create new todo items
- `list_tasks`: Retrieve user's todo items
- `update_task`: Modify existing todo items
- `complete_task`: Mark items as complete/incomplete
- `delete_task`: Remove todo items

### 3. Chat Service
Handles conversation management and database operations:
- Located at: `apps/backend/src/services/chat_service.py`
- Manages conversation lifecycle
- Ensures user ownership validation

### 4. Authentication
JWT-based authentication for user validation:
- Validates user identity
- Ensures conversation access control
- Prevents unauthorized data access

## Development Workflow

### 1. Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Update specifications in `specs/` directory
3. Generate tasks: `/sp.tasks`
4. Implement tasks following the task list
5. Test changes thoroughly
6. Submit pull request

### 2. Running Tests
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_agents/
pytest tests/test_api/test_chat.py
pytest tests/integration/test_agent_integration.py

# Run with coverage
pytest --cov=apps.backend.src --cov-report=html
```

### 3. Local Development Commands
```bash
# Generate tasks from specification
/sp.tasks

# Run specific implementation phases
/sp.red    # Start implementation
/sp.green  # Run tests and validate
```

## Architecture Notes

### Statelessness
- No server-side memory between requests
- All conversation state stored in database
- Each request loads full context from database
- System survives restarts without data loss

### Security
- User authentication required for all endpoints
- Conversation access restricted to owner
- Input sanitization and validation applied
- Rate limiting for AI service protection

### Scalability
- Horizontal scaling ready (no shared memory)
- Database connection pooling configured
- Async processing for better performance
- MCP tools ensure consistent data operations

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
- Check that PostgreSQL is running
- Verify DATABASE_URL in .env file
- Ensure database migrations are up to date

#### 2. OpenAI API Errors
- Verify OPENAI_API_KEY is set correctly
- Check API quota limits
- Ensure network connectivity to OpenAI

#### 3. Authentication Failures
- Verify JWT token format and validity
- Check that user exists in database
- Ensure token was issued for the correct user

#### 4. Agent Response Issues
- Check that MCP tools are properly registered
- Verify tool parameters are correctly formatted
- Review agent system instructions in config

### Getting Help
- Check the API documentation at `/docs`
- Review logs in the console output
- Look at the specification in `specs/002-chat-api-endpoint/`
- Examine the test files for usage examples