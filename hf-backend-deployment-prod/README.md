# Todo Web Application Backend - Production Ready

This is the production-ready backend for the multi-user Todo web application, designed for deployment on Hugging Face Spaces using Docker.

## Features

- User authentication with JWT tokens
- Todo task management with full CRUD operations
- Secure password hashing
- User-specific data isolation
- PostgreSQL database support
- Production-optimized Docker configuration
- Proper error handling and security measures

## Deployment

This backend is configured for deployment on [Hugging Face Spaces](https://huggingface.co/spaces) using the Docker SDK.

### Prerequisites

- Hugging Face account
- PostgreSQL database (consider using Neon Serverless for free tier)

### Environment Variables

Set these environment variables in your Hugging Face Space settings:

```
DATABASE_URL=postgresql://username:password@your-db-url.com:5432/dbname
SECRET_KEY=your-super-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Deployment Steps

1. **Create a new Space on Hugging Face** with Docker SDK
2. **Upload all files in this directory** to your Space
3. **Set environment variables** in Space settings
4. **Wait for the build to complete** (check the logs tab)
5. **Your API will be available** at `https://your-username-todo-backend.hf.space`

## API Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/todos` - Get user's todos
- `POST /api/v1/todos` - Create a new todo
- `GET /api/v1/todos/{id}` - Get a specific todo
- `PUT /api/v1/todos/{id}` - Update a todo
- `DELETE /api/v1/todos/{id}` - Delete a todo
- `PATCH /api/v1/todos/{id}/complete` - Toggle completion status
- `/docs` - Interactive API documentation
- `/health` - Health check endpoint

## Security

- JWT-based authentication with configurable expiration
- Secure password hashing with bcrypt
- SQL injection prevention through SQLModel ORM
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS configuration for API security
- Security headers for XSS and CSRF protection

## Production Features

- Optimized Docker image with minimal attack surface
- Proper logging and monitoring
- Health check endpoints
- Environment-based configuration
- Connection pooling for database operations
- Redis support for caching and sessions

## Support

For support, check the Space logs in the Hugging Face interface. If you encounter issues with the build, verify that:
- All environment variables are properly set
- Database connection string is correct
- No typos in configuration values
- Sufficient hardware resources allocated to the Space
