# Quickstart Guide: Todo AI Chatbot Deployment

## Overview
This guide helps you set up and deploy the Todo AI Chatbot with stateless architecture using FastAPI and OpenAI Agents SDK. The system enables conversational todo management through natural language processing with MCP tools.

## Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL database (Neon Serverless recommended)
- OpenAI API key
- Hugging Face account (for backend deployment)
- Vercel account (for frontend deployment)

## Backend Setup (Hugging Face Spaces)

### 1. Prepare Backend Code
```bash
# Navigate to backend directory
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Backend Configuration (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo

# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Rate Limiting
AI_RATE_LIMIT_PER_MINUTE=30

# CORS Settings
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.com,http://localhost:3000
```

### 3. Create Hugging Face Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose "Docker" as SDK
4. Choose "GPU" or "CPU" tier (CPU is sufficient for this application)
5. Set visibility to "Public" or "Private" as needed

### 4. Add Backend Files to Space Repository
```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-backend
cd todo-ai-backend

# Copy backend files
cp -r /path/to/your/project/apps/backend/src ./src/
cp /path/to/your/project/apps/backend/main.py .
cp /path/to/your/project/apps/backend/Dockerfile .
cp /path/to/your/project/apps/backend/requirements.txt .
cp /path/to/your/project/apps/backend/gunicorn.conf.py .
cp /path/to/your/project/apps/backend/production.py .

# Add environment configuration
cp /path/to/your/project/backend.env.example .env
# Edit .env with your actual configuration values

# Commit and push
git add .
git commit -m "Initial deployment of Todo AI Backend"
git push
```

### 5. Set Environment Variables in Hugging Face Space
In your Hugging Face Space settings:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `SECRET_KEY`: Your secret key for JWT
- `ALLOWED_ORIGINS`: Comma-separated list of frontend domains

## Frontend Setup (Vercel)

### 1. Prepare Frontend Code
```bash
# Navigate to frontend directory
cd apps/frontend

# Install dependencies
npm install
```

### 2. Frontend Configuration (.env.local)
```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend-space.hf.space

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo AI Assistant
NEXT_PUBLIC_BASE_URL=https://your-frontend-domain.vercel.app
```

### 3. Add Domain to OpenAI Allowlist
1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add your Vercel domain: `https://your-frontend-domain.vercel.app`
3. Get your domain key for the NEXT_PUBLIC_OPENAI_DOMAIN_KEY

### 4. Deploy to Vercel
```bash
# Navigate to frontend directory
cd apps/frontend

# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Database Setup (Neon Serverless PostgreSQL)

### 1. Create Neon Database
1. Sign up at https://neon.tech/
2. Create a new project
3. Get the connection string in the format: `postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname`

### 2. Run Migrations
The system will automatically run database migrations on startup. Alternatively, you can run them manually:
```bash
cd apps/backend
python -c "
from sqlmodel import SQLModel
from src.database import engine
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.user import User
from src.models.todo_task import TodoTask

# Create all tables
SQLModel.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
```

## API Usage Examples

### Chat Endpoint
```bash
# Create a new conversation
curl -X POST "https://your-backend-space.hf.space/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'

# Continue an existing conversation
curl -X POST "https://your-backend-space.hf.space/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "message": "Show me my tasks",
    "conversation_id": "789e4567-e89b-12d3-a456-426614174001"
  }'
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

## Testing the Deployment

### 1. Verify Backend Health
```bash
curl https://your-backend-space.hf.space/health
```

### 2. Test Chat Endpoint
```bash
curl -X POST "https://your-backend-space.hf.space/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-test-jwt-token" \
  -d '{
    "message": "Add a task to test the deployment",
    "conversation_id": null
  }'
```

### 3. Verify Frontend Connection
Visit your Vercel frontend URL and test the chat interface with the backend.

## Troubleshooting

### Common Issues

#### 1. ChatKit Domain Not Allowed
- **Symptom**: Frontend shows errors when connecting to AI service
- **Solution**: Add your domain to OpenAI's domain allowlist at https://platform.openai.com/settings/organization/security/domain-allowlist

#### 2. Database Connection Issues
- **Symptom**: Backend returns 500 errors for all requests
- **Solution**: Verify Neon connection string format and SSL settings in DATABASE_URL environment variable

#### 3. Authentication Failures
- **Symptom**: Requests return 403 Forbidden errors
- **Solution**: Verify JWT tokens are properly formatted and user_id in URL matches authenticated user

#### 4. AI Service Unavailability
- **Symptom**: Chat requests return errors or timeout
- **Solution**: Check OpenAI API key validity and account limits; verify rate limits are not exceeded

#### 5. CORS Errors
- **Symptom**: Browser shows CORS errors when calling backend
- **Solution**: Ensure ALLOWED_ORIGINS includes your frontend domain

## Performance & Scaling

### For High Traffic
- Increase worker count in gunicorn.conf.py
- Implement Redis for caching frequently accessed data
- Add CDN for static assets (frontend)
- Monitor database connection pooling

### For Large User Base
- Database connection pooling optimization
- Conversation history truncation for very long conversations
- Asynchronous processing for heavy AI operations
- Monitoring and alerting for system performance

## Security Considerations

### Authentication & Authorization
- All operations require JWT authentication
- User ID validation ensures requests match authenticated user
- Conversation ownership checks prevent cross-user data access
- MCP tools enforce proper authorization for all operations

### Input Validation & Sanitization
- Message length limits (5000 characters)
- Content sanitization to prevent injection attacks
- UUID format validation for user and conversation IDs
- Rate limiting to prevent abuse of AI services