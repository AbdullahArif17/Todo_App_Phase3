---
title: Todo Web Application Backend
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "3.8"
python_version: "3.11"
app_file: app.py
pinned: false
---

# Todo Web Application Backend

This is the backend API for a multi-user Todo web application built with FastAPI and SQLModel.

## Features

- User authentication with JWT tokens
- Todo task management with full CRUD operations
- Secure password hashing
- User-specific data isolation
- PostgreSQL database support
- Production-optimized Docker configuration

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

## Environment Variables

Set these environment variables in your Space settings:

```
DATABASE_URL=postgresql://username:password@your-db-url.com:5432/dbname
SECRET_KEY=your-super-long-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Security

- JWT-based authentication with configurable expiration
- Secure password hashing with bcrypt
- SQL injection prevention through SQLModel ORM
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS configuration for API security
- Security headers for XSS and CSRF protection

## Support

For support, check the Space logs in the Hugging Face interface. If you encounter issues with the build, verify that:
- All environment variables are properly set
- Database connection string is correct
- No typos in configuration values
- Sufficient hardware resources allocated to the Space