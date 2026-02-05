---
title: Todo AI Chatbot Backend
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "3.8"
python_version: "3.11"
app_file: app.py
pinned: false
---

# Todo AI Chatbot Backend - Production Ready

This is the backend API for an AI-powered Todo chatbot that enables natural language interaction with todo management using MCP tools and OpenAI Agents SDK.

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

Set these environment variables in your Space settings:

```
DATABASE_URL=postgresql://username:password@your-db-url.com:5432/dbname
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo
SECRET_KEY=your-super-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.com,http://localhost:3000
AI_RATE_LIMIT_PER_MINUTE=30
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

## Architecture

- **AI Agent**: OpenAI Agents SDK processes natural language and selects appropriate MCP tools
- **MCP Server**: Standardized interface for todo operations accessible by AI agent
- **Database**: Neon Serverless PostgreSQL stores all conversation and task data
- **Stateless**: No server-side memory between requests - all state flows through database
- **Security**: All operations validated through user authentication and authorization

## Support

For support, check the Space logs in the Hugging Face interface. If you encounter issues with the build, verify that:
- All environment variables are properly set (especially OPENAI_API_KEY)
- Database connection string is correct
- No typos in configuration values
- Sufficient hardware resources allocated to the Space
- Frontend domain is added to OpenAI's domain allowlist if using ChatKit