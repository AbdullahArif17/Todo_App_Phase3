# Deployment Plan for Todo AI Chatbot

## Architecture Overview

The Todo AI Chatbot is built with a stateless architecture using FastAPI and the OpenAI Agents SDK (or Groq), with MCP (Model Context Protocol) tools for todo operations. The system is designed for deployment with:

- **Backend**: Deployed to Hugging Face Spaces using Docker
- **Frontend**: Deployed to Vercel as a Next.js application

## Backend Deployment (Hugging Face Spaces)

### Prerequisites
- Hugging Face account
- Groq API key (or OpenAI API key as fallback)
- Neon Serverless PostgreSQL database
- Domain registered with OpenAI ChatKit (for frontend)

### Configuration
Set these environment variables in your Hugging Face Space settings:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# AI Service Configuration (Groq - preferred)
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile
AI_PROVIDER=groq

# AI Service Configuration (OpenAI - fallback)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

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

### Dockerfile Configuration
The Dockerfile is configured for Hugging Face Spaces:
- Uses Python 3.11-slim base image
- Installs all required dependencies
- Copies application code to container
- Sets up non-root user for security
- Exposes port 7860
- Includes health check

### Deployment Steps
1. Create a new Hugging Face Space with Docker option
2. Add the Dockerfile and source code to the repository
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

### Domain Registration
Before deploying to Vercel, register your domain with OpenAI:
1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add your Vercel domain: `https://your-project-name.vercel.app`
3. Get the domain key and use it as NEXT_PUBLIC_OPENAI_DOMAIN_KEY

### Deployment Steps
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

### Other Endpoints
- `/health` - Health check for the backend service
- `/api/{user_id}/conversations` - Get user's conversations
- `/api/{user_id}/conversations/{conversation_id}/messages` - Get conversation messages
- `/api/{user_id}/search` - Search conversations by content

## MCP Tools Integration

The system uses MCP tools for all todo operations:
- `add_task` - Create new todo items
- `list_tasks` - Retrieve user's todo items
- `update_task` - Update existing todo items
- `complete_task` - Mark todo items as complete/incomplete
- `delete_task` - Remove todo items

The AI agent delegates all data operations to these tools rather than accessing the database directly.

## Security Features

- JWT-based authentication with configurable expiration
- User ownership validation for all conversation access
- Input sanitization to prevent injection attacks
- Rate limiting for API usage per user
- CORS configuration for frontend security
- MCP tool-first architecture ensuring all operations are properly authorized

## Performance & Scalability

- Stateless design supports horizontal scaling
- Conversation data persisted in database (survives server restarts)
- Efficient database queries with proper indexing
- Connection pooling for database operations
- Proper caching strategies where appropriate

## Monitoring & Logging

- Health check endpoints for service monitoring
- Comprehensive logging for debugging and monitoring
- Tool usage tracking for analytics
- Performance metrics collection
- Error tracking and alerting

## Troubleshooting

### Common Issues

1. **Domain Not Registered**: If ChatKit shows errors, ensure your domain is registered with OpenAI
2. **Database Connection**: Verify Neon connection string format and SSL settings
3. **Authentication Failures**: Check JWT tokens and ensure user_id matches authenticated user
4. **AI Service Unavailability**: Verify API keys and account limits for Groq/OpenAI
5. **CORS Errors**: Ensure ALLOWED_ORIGINS includes your frontend domain

### Health Checks
- Backend: `https://your-backend-space.hf.space/health`
- Frontend: Check browser console for any errors
- Database: Verify connection with the provided DATABASE_URL

## Environment-Specific Notes

### Production Environment
- Set ENVIRONMENT=production
- DEBUG=false
- Proper rate limiting configuration
- SSL certificates for secure connections

### Development Environment
- Use localhost URLs for backend
- Lower rate limits for testing
- More verbose logging
- Hot reloading enabled