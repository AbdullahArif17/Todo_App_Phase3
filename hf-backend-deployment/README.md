# Todo Web Application Backend

This is the production-ready backend for the multi-user Todo web application, designed for deployment on Hugging Face Spaces using Docker.

## Features

- User authentication with JWT tokens
- Todo task management with full CRUD operations
- Secure password hashing
- User-specific data isolation
- PostgreSQL database support
- Production-optimized Docker configuration

## Deployment

This backend is designed for deployment on [Hugging Face Spaces](https://huggingface.co/spaces) using the Docker SDK.

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
```

### Deployment Steps

1. Create a new Space on Hugging Face with Docker SDK
2. Upload all files in this directory to your Space
3. Set the environment variables in Space settings
4. Wait for the build to complete
5. Your API will be available at `https://your-username-your-space-name.hf.space`

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
- CORS configuration for API security
- Input validation and sanitization

## Support

For support, check the Space logs in the Hugging Face interface.