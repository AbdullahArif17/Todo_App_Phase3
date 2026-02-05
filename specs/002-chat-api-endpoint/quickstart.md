# Quickstart Guide: Todo AI Chatbot

## Overview
This guide helps you set up and run the Todo AI Chatbot with MCP tools and OpenAI Agents SDK integration.

## Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL database (Neon Serverless recommended)
- OpenAI API key
- Hugging Face account (for backend deployment)
- Vercel account (for frontend deployment)

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp ../backend.env.example .env
# Edit .env with your actual configuration values
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd apps/frontend

# Install dependencies
npm install

# Create environment file
cp ../frontend.env.example .env.local
# Edit .env.local with your actual configuration values
```

## Configuration

### Backend Configuration (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo

# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000
```

### Frontend Configuration (.env.local)
```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:7860
NEXT_PUBLIC_API_BASE_URL=http://localhost:7860

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo AI Assistant
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## Running Locally

### 1. Start the Backend
```bash
cd apps/backend
source venv/bin/activate  # Activate virtual environment
uvicorn src.main:app --reload --port 7860
```

### 2. Start the Frontend
```bash
cd apps/frontend
npm run dev
```

## API Usage

### Chat Endpoint
```bash
# Create a new conversation
curl -X POST "http://localhost:7860/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "message": "Add a task to buy groceries"
  }'

# Continue an existing conversation
curl -X POST "http://localhost:7860/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "message": "Show me my tasks",
    "conversation_id": "789e4567-e89b-12d3-a456-426614174001"
  }'
```

## MCP Server Tools

The system exposes the following tools via MCP for the AI agent:

### add_task
- Creates a new task for a user
- Parameters: user_id (string), title (string), description (optional string)

### list_tasks
- Lists tasks for a user
- Parameters: user_id (string), limit (optional integer), offset (optional integer)

### update_task
- Updates an existing task
- Parameters: user_id (string), task_id (string), title (optional string), description (optional string), is_completed (optional boolean)

### complete_task
- Marks a task as complete or incomplete for a user
- Parameters: user_id (string), task_id (string), is_completed (optional boolean, default: true)

### delete_task
- Deletes a task for a user
- Parameters: user_id (string), task_id (string)

## OpenAI Agent Integration

The system uses OpenAI Agents SDK to process natural language requests:

1. User sends a message to the chat endpoint
2. The system loads conversation history from the database
3. The AI agent processes the message with context
4. The agent determines which MCP tools to call
5. MCP tools execute the requested operations
6. The agent generates a natural language response
7. The response is stored in the database and returned to the user

## Development Workflow

### 1. Adding New Features
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Update specifications in `specs/` directory
3. Generate plan: `/sp.plan`
4. Generate tasks: `/sp.tasks`
5. Implement tasks following the task list
6. Test changes thoroughly
7. Submit pull request

### 2. Running Tests
```bash
# Backend tests
cd apps/backend
pytest tests/

# Frontend tests
cd apps/frontend
npm run test
```

### 3. Local Development Commands
```bash
# Generate specification
/sp.specify

# Generate plan
/sp.plan

# Generate tasks
/sp.tasks

# Implement tasks
/sp.implement
```

## Deployment

### Backend to Hugging Face Spaces
1. Create a Hugging Face Space with Docker option
2. Add the Dockerfile and app.py files to the repository
3. Set environment variables in Space settings
4. Push code to the Space repository

### Frontend to Vercel
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel project settings
3. Deploy automatically on pushes to main branch

## Troubleshooting

### Common Issues

#### 1. ChatKit Domain Not Allowed
- Solution: Add your domain to OpenAI's domain allowlist at https://platform.openai.com/settings/organization/security/domain-allowlist

#### 2. Database Connection Issues
- Solution: Verify Neon connection string and SSL settings
- Check that the DATABASE_URL is properly formatted

#### 3. CORS Errors
- Solution: Ensure ALLOWED_ORIGINS includes your frontend domain

#### 4. AI Service Unavailable
- Solution: Verify OPENAI_API_KEY is correct and has sufficient credits
- Check rate limits in your OpenAI account

#### 5. Authentication Failures
- Solution: Verify JWT token is valid and properly formatted
- Check that user_id in URL matches authenticated user