# Todo AI Chatbot - Deployment Guide

## Overview
This guide provides instructions for deploying the Todo AI Chatbot to Hugging Face Spaces (backend) and Vercel (frontend).

## Architecture
- **Backend**: FastAPI application deployed to Hugging Face Spaces
- **Frontend**: Next.js application deployed to Vercel
- **Database**: Neon Serverless PostgreSQL
- **AI**: OpenAI Agents SDK with MCP tools

## Backend Deployment (Hugging Face Spaces)

### 1. Prerequisites
- Hugging Face account
- OpenAI API key
- Neon PostgreSQL database URL
- Domain for OpenAI ChatKit (if using)

### 2. Create Hugging Face Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose "Docker" as SDK
4. Choose "GPU" or "CPU" tier (CPU is sufficient for this application)
5. Set visibility to "Public" or "Private" as needed

### 3. Configure Environment Variables
In your Hugging Face Space settings, add the following environment variables:

```env
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
SECRET_KEY=your-super-secret-key-change-in-production
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.com,http://localhost:3000
```

### 4. Deploy Code
1. Clone your Space repository:
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-ai-backend
cd todo-ai-backend
```

2. Copy the following files to your Space repository:
- `Dockerfile`
- `app.py`
- `apps/backend/src/` (entire directory)
- `hf_requirements.txt` (rename to `requirements.txt`)

3. Commit and push:
```bash
git add .
git commit -m "Initial deployment"
git push
```

### 5. Verify Backend
- Access the Space URL: `https://YOUR_USERNAME-space-name.hf.space`
- Test the health endpoint: `https://YOUR_USERNAME-space-name.hf.space/health`
- Test the chat endpoint: `https://YOUR_USERNAME-space-name.hf.space/api/v1/chat`

## Frontend Deployment (Vercel)

### 1. Prerequisites
- Vercel account
- OpenAI ChatKit domain key (from security settings)

### 2. Add Domain to OpenAI Allowlist
1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. Add your Vercel domain: `https://your-project-name.vercel.app`
4. Save changes

### 3. Deploy to Vercel
1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Navigate to frontend directory:
```bash
cd apps/frontend
```

3. Deploy:
```bash
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

### 4. Configure Environment Variables
In your Vercel project settings, add these environment variables:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend-space.hf.space
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here
NEXT_PUBLIC_APP_NAME=Todo AI Assistant
NEXT_PUBLIC_APP_DESCRIPTION=AI-powered todo management with natural language
```

## Configuration Files

### Backend Environment (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname
NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1500

# AI Agent Configuration
AI_AGENT_NAME=Todo Assistant
AI_AGENT_MODEL=gpt-4-turbo
AI_AGENT_TEMPERATURE=0.7
AI_AGENT_MAX_TOKENS=1500
AI_AGENT_INSTRUCTIONS=You are a helpful todo management assistant that helps users manage their tasks using natural language. You can help create, update, delete, and list todos. You have access to tools for these operations. Always respond in a friendly and helpful manner.

# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
AI_RATE_LIMIT_PER_MINUTE=30

# CORS Settings
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.com,http://localhost:3000
```

### Frontend Environment (.env.local)
```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend-space.hf.space
NEXT_PUBLIC_API_BASE_URL=https://your-backend-space.hf.space/api

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo AI Assistant
NEXT_PUBLIC_APP_DESCRIPTION=AI-powered todo management with natural language
NEXT_PUBLIC_BASE_URL=https://your-frontend-domain.vercel.app

# Authentication
NEXTAUTH_URL=https://your-frontend-domain.vercel.app
NEXTAUTH_SECRET=your-nextauth-secret-here

# Development Overrides
NEXT_PUBLIC_DEV_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_DEV_MODE=false
```

## Deployment Sequence

### Phase 1: Backend Deployment
1. Set up Neon Serverless PostgreSQL database
2. Configure Hugging Face Space with Dockerfile
3. Set environment variables in Space settings
4. Deploy backend to Hugging Face Space
5. Verify backend API is accessible

### Phase 2: Frontend Deployment
1. Add Vercel domain to OpenAI domain allowlist
2. Deploy frontend to Vercel
3. Set environment variables in Vercel settings
4. Verify ChatKit integration works

### Phase 3: Integration Testing
1. Test full conversation flow
2. Verify authentication works
3. Test all MCP tools via AI agent
4. Verify conversation persistence

## Health Checks & Monitoring

### Backend Health Endpoints
- `/health` - Basic health check
- `/api/v1/chat` - Chat functionality
- Database connection validation

### Frontend Monitoring
- Console error logging
- Network request monitoring
- User session tracking

## Troubleshooting

### Common Issues
1. **ChatKit Domain Not Allowed**: Verify domain is added to OpenAI allowlist
2. **Database Connection Issues**: Check Neon connection string and SSL settings
3. **CORS Errors**: Verify ALLOWED_ORIGINS includes your frontend domain
4. **AI Service Unavailable**: Check OPENAI_API_KEY and rate limits

### Logs Access
- Hugging Face Spaces: Access through Space interface
- Vercel: Access through Vercel dashboard
- Database: Access through Neon dashboard

## Scaling Considerations

### Backend Scaling
- Hugging Face Spaces automatically scales containers
- Neon Serverless PostgreSQL scales automatically
- Add Redis for session caching if needed for high traffic

### Rate Limiting
- Per-user API rate limits configured
- AI service usage monitoring
- Database connection pooling