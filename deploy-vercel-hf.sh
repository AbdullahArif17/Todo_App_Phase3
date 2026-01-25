#!/bin/bash

# Deployment script for Todo Web Application to Vercel + Hugging Face Spaces

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting deployment to Vercel + Hugging Face Spaces..."

# Function to check if a command exists
command_exists() {
  command -v "$@" > /dev/null 2>&1
}

# Check prerequisites
if ! command_exists git; then
  echo "❌ Error: git is not installed or not in PATH"
  exit 1
fi

if ! command_exists npm; then
  echo "❌ Error: npm is not installed or not in PATH"
  exit 1
fi

echo "✅ Prerequisites check passed"

# Function to deploy backend to Hugging Face Spaces
deploy_backend() {
  echo "📦 Setting up backend for Hugging Face Spaces deployment..."

  # Navigate to backend directory
  cd apps/backend

  # Create/update Dockerfile for Hugging Face Spaces
  cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port for Hugging Face Spaces
EXPOSE 7860

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
EOF

  echo "✅ Backend Dockerfile created for Hugging Face Spaces"

  # Create Hugging Face Spaces configuration
  cat > README.md << 'EOF'
---
title: Todo Web Application Backend
emoji: 📝
colorFrom: blue
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
---

# Todo Web Application Backend

This is the backend API for a multi-user Todo web application built with FastAPI and SQLModel.

## API Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/todos` - Get user's todos
- `POST /api/v1/todos` - Create a new todo
- `PUT /api/v1/todos/{id}` - Update a todo
- `DELETE /api/v1/todos/{id}` - Delete a todo
- `PATCH /api/v1/todos/{id}/complete` - Toggle completion status

## Environment Variables

- `DATABASE_URL`: PostgreSQL database URL
- `SECRET_KEY`: JWT secret key (required)
- `ALGORITHM`: JWT algorithm (defaults to HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (defaults to 30)

## Features

- Multi-user authentication with JWT
- Secure password hashing
- User-specific data isolation
- Full CRUD operations for todo tasks
- Production-ready security features
EOF

  echo "✅ Hugging Face Spaces README created"

  # Create a simple app.py for Hugging Face Spaces compatibility
  cat > app.py << 'EOF'
import os
import uvicorn
from src.api.main import app

# For Hugging Face Spaces compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
EOF

  echo "✅ Backend setup for Hugging Face Spaces completed"
  cd ../..
}

# Function to prepare frontend for Vercel
prepare_frontend() {
  echo "📦 Preparing frontend for Vercel deployment..."

  cd apps/frontend

  # Update package.json for Vercel deployment
  if [ -f "package.json" ]; then
    # Backup original
    cp package.json package.json.bak

    # Update build script for Vercel
    sed -i 's/"build": "next build"/"build": "next build"/' package.json
  fi

  # Ensure next.config.js is properly configured for Vercel
  cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-downgrade'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ]
      }
    ]
  },
  // Image optimization configuration
  images: {
    domains: ['localhost', '127.0.0.1', 'images.unsplash.com'],
    formats: ['image/webp'],
  },
  // Enable compression
  compress: true,
};

module.exports = nextConfig;
EOF

  echo "✅ Frontend prepared for Vercel deployment"
  cd ../..
}

# Function to display deployment instructions
display_instructions() {
  echo ""
  echo "🎉 Deployment preparation completed!"
  echo ""
  echo "##################################################"
  echo "# DEPLOYMENT INSTRUCTIONS"
  echo "##################################################"
  echo ""
  echo "1. BACKEND DEPLOYMENT (Hugging Face Spaces):"
  echo "   a. Go to https://huggingface.co/spaces"
  echo "   b. Create a new Space with these settings:"
  echo "      - Name: your-username/todo-backend"
  echo "      - SDK: Docker"
  echo "      - Hardware: CPU Basic (or higher)"
  echo "      - Visibility: Public"
  echo "   c. Upload the contents of apps/backend/ to your Space"
  echo "   d. Set environment variables in Space settings:"
  echo "      - DATABASE_URL=your_postgresql_connection_string"
  echo "      - SECRET_KEY=your_very_long_secret_key"
  echo "      - ALGORITHM=HS256"
  echo "      - ACCESS_TOKEN_EXPIRE_MINUTES=30"
  echo "      - ENVIRONMENT=production"
  echo "      - DEBUG=False"
  echo ""
  echo "2. FRONTEND DEPLOYMENT (Vercel):"
  echo "   a. Go to https://vercel.com"
  echo "   b. Create new project and import your repository"
  echo "   c. Set these environment variables in Vercel dashboard:"
  echo "      - NEXT_PUBLIC_API_BASE_URL=https://your-username-todo-backend.hf.space"
  echo "      - NODE_ENV=production"
  echo "   d. Deploy the project"
  echo ""
  echo "3. CONFIGURATION:"
  echo "   - Replace 'your-username' with your actual Hugging Face username"
  echo "   - Use a strong SECRET_KEY (at least 32 random characters)"
  echo "   - For DATABASE_URL, consider using Neon Serverless PostgreSQL"
  echo ""
  echo "4. VERIFICATION:"
  echo "   - Backend API: https://your-username-todo-backend.hf.space/docs"
  echo "   - Frontend: Your Vercel deployment URL"
  echo "   - Test registration and login functionality"
  echo ""
  echo "✅ Your application is now ready for deployment!"
  echo "##################################################"
}

# Main execution
main() {
  echo "Preparing application for Vercel + Hugging Face Spaces deployment..."

  # Deploy backend
  deploy_backend

  # Prepare frontend
  prepare_frontend

  # Display instructions
  display_instructions
}

# Run main function
main "$@"