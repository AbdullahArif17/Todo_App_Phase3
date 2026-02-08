# Todo AI Chatbot Deployment Guide

## Backend Deployment (Hugging Face Spaces)

### Prerequisites
- Hugging Face account
- OpenAI API key (or Groq API key)
- Neon Serverless PostgreSQL database
- Domain registered with OpenAI ChatKit (for frontend)

### Configuration
Set these environment variables in your Hugging Face Space settings:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# AI Service Configuration (Choose one)
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile
AI_PROVIDER=groq

# OR for OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
AI_PROVIDER=openai

# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production
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

### Steps
1. Create a new Hugging Face Space with Docker option
2. Copy the files from `apps/backend/` to the Space repository
3. Set environment variables in Space settings
4. Push code to the repository

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account
- Domain registered with OpenAI ChatKit
- Backend API endpoint URL

### Configuration
Set these environment variables in your Vercel project settings:

```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend-space.hf.space

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo AI Assistant
NEXT_PUBLIC_BASE_URL=https://your-frontend-domain.vercel.app
```

### Steps
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel project settings
3. Deploy automatically on pushes to main branch

## API Endpoints

### Chat Endpoint
- **Method**: POST
- **Path**: `/api/{user_id}/chat`
- **Authentication**: JWT Bearer token required
- **Request Body**:
  ```json
  {
    "message": "string (required)",
    "conversation_id": "string (optional, UUID format)"
  }
  ```
- **Response**:
  ```json
  {
    "conversation_id": "string (UUID format)",
    "response": "string (AI-generated response)",
    "message_id": "string (UUID format of the assistant's response message)"
  }
  ```

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │    Neon DB      │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │  (PostgreSQL)   │
│  (Frontend)     │     │  │  POST /api/{user_id}/chat             │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │  - tasks        │
│                 │     │                  │                           │     │  - conversations│
│                 │     │                  ▼                           │     │  - messages     │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│                 │     │  │      OpenAI Agents SDK                 │  │     │                 │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                 │  │     │                 │
│                 │     │  │  (MCP Tools for Task Operations)       │  │     │                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

## MCP Tools Available

The system exposes the following tools via MCP for the AI agent:

### add_task
- Creates a new task for a user
- Parameters: user_id (string), title (string), description (optional string)

### list_tasks
- Lists tasks for a user
- Parameters: user_id (string), limit (optional integer), offset (optional integer)

### update_task
- Updates an existing task for a user
- Parameters: user_id (string), task_id (string), title (optional string), description (optional string), is_completed (optional boolean)

### complete_task
- Marks a task as complete or incomplete for a user
- Parameters: user_id (string), task_id (string), is_completed (optional boolean, default: true)

### delete_task
- Deletes a task for a user
- Parameters: user_id (string), task_id (string)

## Security Features

- JWT-based authentication with configurable expiration
- User ownership validation for all conversation access
- MCP tool-first architecture ensuring all operations are properly authorized
- SQL injection prevention through SQLModel ORM
- Rate limiting to prevent abuse of AI services
- Input validation and sanitization including prompt injection prevention
- CORS configuration for API security
- Conversation isolation to prevent cross-user data access

## Performance & Scalability

- Stateless design supports horizontal scaling
- Conversation data persisted in database (survives server restarts)
- Efficient database queries with proper indexing
- Connection pooling for database operations
- Proper caching strategies where appropriate
- Circuit breaker pattern for AI service calls
- Retry logic with exponential backoff for failed calls

## Monitoring & Logging

- Health check endpoints: `/health` and `/api/health`
- Comprehensive logging for debugging and monitoring
- Tool usage tracking for analytics
- Performance metrics collection
- Error tracking and alerting