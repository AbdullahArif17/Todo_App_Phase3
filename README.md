# Multi-User Todo Web Application

A full-stack todo application with user authentication, task management, and responsive UI.

## Features

- User registration and authentication
- Create, read, update, and delete todo tasks
- Mark tasks as complete/incomplete
- User-specific task isolation
- Responsive UI for desktop and mobile
- Production-ready security and performance features

## Tech Stack

- **Frontend**: Next.js 14+, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, SQLModel
- **Database**: PostgreSQL (with Neon Serverless option)
- **Authentication**: JWT-based with secure password hashing
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Nginx
- **Caching**: Redis

## Architecture

The application follows a monorepo structure with clean architecture principles:

```
apps/
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/      # Pages using App Router
│   │   ├── components/
│   │   └── services/
│   └── package.json
└── backend/           # FastAPI application
    ├── src/
    │   ├── models/    # SQLModel database models
    │   ├── schemas/   # Pydantic request/response schemas
    │   ├── services/  # Business logic
    │   ├── api/       # API routes
    │   └── core/      # Configuration and security
    ├── requirements.txt
    └── alembic/       # Database migrations
```

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- At least 2GB RAM available
- Port 80 and 443 available (or 3000 and 8000 for development)

### Production Setup

1. **Configure environment variables**:
   ```bash
   cp .env.production .env
   # Edit the .env file with your production settings
   # Make sure to set a strong SECRET_KEY value
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. **Run database migrations**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

### Production Features

- ✅ Complete user authentication system (register/login)
- ✅ Secure JWT-based authentication with proper expiration
- ✅ User-specific data isolation (users only see their own tasks)
- ✅ Responsive UI for desktop and mobile devices
- ✅ Production-grade security (CORS, rate limiting, input validation)
- ✅ Docker containerization with optimized images
- ✅ Nginx reverse proxy for performance and security
- ✅ PostgreSQL database with connection pooling
- ✅ Redis for caching and session storage
- ✅ Structured logging with JSON format
- ✅ Health check endpoints
- ✅ Environment-based configuration
- ✅ API documentation with Swagger UI

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Todo Management

- `GET /api/v1/todos` - Get user's todos
- `POST /api/v1/todos` - Create a new todo
- `GET /api/v1/todos/{id}` - Get a specific todo
- `PUT /api/v1/todos/{id}` - Update a todo
- `DELETE /api/v1/todos/{id}` - Delete a todo
- `PATCH /api/v1/todos/{id}/complete` - Toggle completion status

## Security Features

- JWT-based authentication with proper token expiration
- Secure password hashing with bcrypt
- SQL injection prevention through ORM
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS configuration for API security
- User data isolation (each user sees only their own tasks)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@your-db-url.com:5432/dbname
SECRET_KEY=your-super-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
NODE_ENV=production
```

## Deployment Options

### Hugging Face Spaces (Backend) + Vercel (Frontend) - Recommended
- Backend: Deploy to Hugging Face Spaces using Docker SDK
- Frontend: Deploy to Vercel with Next.js configuration
- Database: PostgreSQL (Neon Serverless recommended)

### Self-Hosting
- Use docker-compose.prod.yml for local deployment
- Configure with your own domain and SSL
- Set up PostgreSQL database

## Performance Optimizations

- Database connection pooling
- Gzip compression for API responses
- Optimized Docker images
- Database query optimization with proper indexing
- Next.js production optimizations
- Redis for caching and session storage

## Demo Credentials

For testing purposes, a demo user is created during deployment:

- Email: `demo@example.com`
- Password: `demo123`

## Notes:
- The application uses SQLite by default for development (as configured in the backend)
- For production, PostgreSQL is configured in the docker-compose.prod.yml
- All environment variables can be set in `.env` files for both frontend and backend
- The production setup includes security headers, SSL termination (via Nginx), and optimized caching

## 🚀 Production Ready Status

The application is now **completely production-ready** with all security, performance, and operational features implemented.

### Backend Deployment
- Located in `apps/backend/` directory
- Ready for deployment to Hugging Face Spaces with Docker SDK
- Includes optimized Docker configuration
- Proper security headers and middleware
- Production-optimized dependencies

### Frontend Deployment
- Located in `apps/frontend/` directory
- Ready for deployment to Vercel or other Next.js hosting platforms
- Environment-based API configuration
- Responsive design for all devices

### Deployment Steps:
1. **Backend**: Upload `apps/backend/` directory to Hugging Face Spaces
2. **Frontend**: Deploy `apps/frontend/` to Vercel with proper environment variables
3. **Set environment variables** as documented in the deployment section
4. **Application will be accessible** at your domain URLs

### Production Features:
- ✅ Complete authentication system (register/login)
- ✅ Secure JWT-based authentication with proper expiration
- ✅ Full CRUD operations for todo tasks
- ✅ User-specific data isolation (users only see their own tasks)
- ✅ Production-grade security (CORS, rate limiting, input validation)
- ✅ Docker containerization with optimized images
- ✅ Proper error handling and logging
- ✅ Health check endpoints
- ✅ Environment-based configuration
- ✅ API documentation with Swagger UI

The application is ready for immediate production deployment! 🎉