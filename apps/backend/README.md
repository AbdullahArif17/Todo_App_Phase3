# Todo AI Backend

This is the backend service for the Todo AI Chatbot that provides a stateless chat API endpoint with AI agent integration for todo management.

## Features

- Natural language processing for todo management via AI agent
- MCP (Model Context Protocol) server with standardized tools for todo operations
- OpenAI Agents SDK integration for intelligent task processing
- Stateless chat architecture with no server-side memory between requests
- Conversation persistence through database storage
- User authentication with JWT tokens
- User-specific data isolation for conversations and tasks
- PostgreSQL database support
- Production-optimized Docker configuration

## Architecture

The system implements a stateless chat architecture using:
- **FastAPI**: High-performance web framework
- **OpenAI Agents SDK**: AI agent for natural language processing
- **MCP Server**: Model Context Protocol server exposing todo operations as tools
- **SQLModel**: Typed SQL models with SQLAlchemy compatibility
- **Neon Serverless PostgreSQL**: Cloud-native database with auto-scaling

## API Endpoints

- `POST /api/{user_id}/chat` - Process natural language messages through AI agent
- `GET /api/{user_id}/conversations` - Get user's conversations
- `GET /api/{user_id}/conversations/{conversation_id}/messages` - Get conversation messages
- `GET /api/{user_id}/search` - Search conversations and messages
- `GET /health` - Health check endpoint
- `/docs` - Interactive API documentation

## MCP Tools Available

- `add_task` - Add a new task for a user
- `list_tasks` - List tasks for a user
- `update_task` - Update an existing task for a user
- `complete_task` - Mark a task as complete or incomplete for a user
- `delete_task` - Delete a task for a user

## Environment Variables

Set these environment variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo

# Security Configuration
SECRET_KEY=your-super-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS Settings
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.com,http://localhost:3000

# Rate Limiting
AI_RATE_LIMIT_PER_MINUTE=30
```

## Deployment to Hugging Face Spaces

This repository is configured for deployment to Hugging Face Spaces using Docker.

### Requirements
- Dockerfile at repository root
- Proper environment configuration
- All dependencies listed in requirements.txt

### Steps
1. Create a Hugging Face Space with Docker option
2. Add the Dockerfile and app.py files to the repository
3. Set environment variables in Space settings
4. Push code to the Space repository

## Local Development

### Running the Application
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 7860
```

### Testing
```bash
cd apps/backend
pytest tests/
```

## Security

- JWT-based authentication with configurable expiration
- User ownership validation for all conversation access
- MCP tool-first architecture ensuring all operations are properly authorized
- SQL injection prevention through SQLModel ORM
- Rate limiting to prevent abuse of AI services
- Input validation and sanitization including prompt injection prevention
- CORS configuration for API security
- Security headers for XSS and CSRF protection
- Conversation isolation to prevent cross-user data access