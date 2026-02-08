# Todo AI Frontend

This is the frontend application for the Todo AI Chatbot that provides a conversational interface for managing todos using natural language.

## Features

- AI-powered chat interface using OpenAI ChatKit
- Real-time conversation with todo management capabilities
- User authentication and conversation management
- Responsive design with modern UI components
- Natural language processing for todo operations
- Conversation history and search functionality
- Secure integration with backend AI services

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **UI Library**: Tailwind CSS with custom components
- **State Management**: React Context API
- **API Integration**: Built-in fetch with proper error handling
- **Authentication**: JWT-based authentication
- **Chat Interface**: OpenAI ChatKit integration

## Environment Variables

Create a `.env.local` file with the following variables:

```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_URL=https://your-backend-space.hf.space
NEXT_PUBLIC_API_BASE_URL=https://your-backend-space.hf.space/api

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo AI Assistant
NEXT_PUBLIC_BASE_URL=https://your-frontend-domain.vercel.app
NEXT_PUBLIC_APP_DESCRIPTION=AI-powered todo management with natural language
```

## ChatKit Domain Configuration

Before deploying, you must add your domain to OpenAI's domain allowlist:

1. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
2. Add your domain: `https://your-frontend-domain.vercel.app`
3. Use the domain key in `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`

## Local Development

### Setup
```bash
cd apps/frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

### Building
```bash
npm run build
```

### Testing
```bash
npm run test
```

## Deployment to Vercel

### Prerequisites
- Vercel account
- Domain added to OpenAI's allowlist for ChatKit

### Steps
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel project settings
3. Deploy automatically on pushes to main branch

## API Integration

The frontend communicates with the backend through:
- `POST /api/{user_id}/chat` - Send messages to the AI assistant
- `GET /api/{user_id}/conversations` - Get conversation history
- `GET /api/{user_id}/conversations/{conversation_id}/messages` - Get specific conversation messages
- `GET /api/{user_id}/search` - Search conversations and messages
- `/health` - Health check endpoint

## User Flows

### New Conversation
1. User sends initial message to AI assistant
2. System creates new conversation
3. AI processes natural language and responds
4. Conversation persists in database

### Existing Conversation
1. User continues with existing conversation ID
2. System loads conversation history
3. AI maintains context across exchanges
4. Responses are added to conversation history

### Security
- JWT token authentication for all API calls
- User-specific conversation isolation
- Input sanitization for message content
- Rate limiting for API usage