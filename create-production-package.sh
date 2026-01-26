#!/bin/bash

# Script to create a production-ready package for Hugging Face Spaces deployment

set -e  # Exit immediately if a command exits with a non-zero status

echo "📦 Creating production package for Hugging Face Spaces deployment..."

# Create the deployment directory
HF_DIR="hf-backend-deployment-clean"
rm -rf "$HF_DIR"
mkdir -p "$HF_DIR"

# Copy essential files only
cp apps/backend/Dockerfile.hf "$HF_DIR/Dockerfile"
cp apps/backend/requirements-minimal.txt "$HF_DIR/requirements.txt"
cp apps/backend/app.py "$HF_DIR/"
cp apps/backend/.dockerignore "$HF_DIR/"

# Create clean source structure
mkdir -p "$HF_DIR/src"

# Copy source files while excluding cache and unnecessary files
rsync -av --exclude="__pycache__" --exclude="*.pyc" --exclude="*.pyo" --exclude=".git" --exclude="node_modules" apps/backend/src/ "$HF_DIR/src/"

# Copy alembic directory if it exists
if [ -d "apps/backend/alembic" ]; then
  mkdir -p "$HF_DIR/alembic"
  rsync -av --exclude="__pycache__" --exclude="*.pyc" --exclude="*.pyo" apps/backend/alembic/ "$HF_DIR/alembic/"
fi

# Create a clean README
cat > "$HF_DIR/README.md" << 'EOF'
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
```

### Deployment Steps

1. **Create a new Space on Hugging Face** with Docker SDK
2. **Upload all files in this directory** to your Space
3. **Set environment variables** in Space settings
4. **Wait for the build to complete** (check the logs tab)
5. **Your API will be available** at `https://your-username-your-space-name.hf.space`

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

## Support

For support, check the Space logs in the Hugging Face interface. If you encounter issues with the build, verify that:
- All environment variables are properly set
- Database connection string is correct
- No typos in configuration values
- Sufficient hardware resources allocated to the Space
EOF

echo "✅ Production package created in $HF_DIR/"
echo "📁 Contents:"
ls -la "$HF_DIR/"
echo "📦 Source structure:"
find "$HF_DIR/src" -type f | head -20

echo ""
echo "🚀 Package ready for deployment to Hugging Face Spaces!"
echo ""
echo "To deploy:"
echo "1. Create a new Space on Hugging Face with Docker SDK"
echo "2. Upload all files in the $HF_DIR directory to your Space"
echo "3. Set environment variables in Space settings"
echo "4. Wait for build to complete"