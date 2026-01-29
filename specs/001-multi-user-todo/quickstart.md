# Quickstart Guide: Multi-User Todo Web Application

**Feature**: 001-multi-user-todo
**Date**: 2026-01-20
**Guide**: Claude

## Overview

This guide provides quick setup instructions for the multi-user Todo web application featuring Next.js frontend, FastAPI backend, and Neon Serverless PostgreSQL database.

## Prerequisites

- Node.js 18+ for frontend development
- Python 3.11+ for backend development
- Docker (for local database setup)
- Git for version control
- A Neon account for PostgreSQL hosting (or local PostgreSQL for development)

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd apps/backend
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment variables file:

```bash
cp .env.example .env
```

Configure environment variables in `.env`:

```env
DATABASE_URL="postgresql://username:password@localhost:5432/todo_app_dev"
SECRET_KEY="your-super-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
NEON_DATABASE_URL="your-neon-database-url"  # For production
```

### 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd apps/frontend
```

Install dependencies:

```bash
npm install
# or
yarn install
```

Create environment variables file:

```bash
cp .env.example .env.local
```

Configure environment variables in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL="http://localhost:7860/api/v1"
NEXTAUTH_SECRET="your-nextauth-secret"
NEXTAUTH_URL="http://localhost:3000"
```

## Running the Application

### 1. Start the Database

If using local PostgreSQL:

```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # On Ubuntu/Debian
brew services start postgresql   # On macOS
```

If using Neon, ensure your database is running in the cloud.

### 2. Run Database Migrations

From the backend directory:

```bash
cd apps/backend
source venv/bin/activate
alembic upgrade head
```

### 3. Start the Backend Server

From the backend directory:

```bash
cd apps/backend
source venv/bin/activate
uvicorn src.api.main:app --reload --port 7860
```

### 4. Start the Frontend Server

From the frontend directory:

```bash
cd apps/frontend
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000` and the backend API at `http://localhost:7860`.

## Key Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login existing user

### Todo Operations
- `GET /api/v1/todos` - Get user's todos
- `POST /api/v1/todos` - Create new todo
- `PUT /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo
- `PATCH /api/v1/todos/{id}/complete` - Toggle completion status

## Development Workflow

### Backend Development
1. Make changes to Python files in `apps/backend/src/`
2. The server automatically reloads due to `--reload` flag
3. Run tests: `pytest`

### Frontend Development
1. Make changes to React components in `apps/frontend/src/`
2. The server automatically reloads
3. Run tests: `npm test` or `yarn test`

### Database Changes
1. Modify data models in `apps/backend/src/models/`
2. Generate migration: `alembic revision --autogenerate -m "description of change"`
3. Apply migration: `alembic upgrade head`

## Testing

### Backend Tests
From the backend directory:
```bash
cd apps/backend
source venv/bin/activate
pytest
```

### Frontend Tests
From the frontend directory:
```bash
cd apps/frontend
npm test
# or
yarn test
```

## Deployment

### Build for Production

Frontend:
```bash
cd apps/frontend
npm run build
```

Backend:
```bash
cd apps/backend
# Ensure production dependencies are installed
pip install -r requirements.txt
```

### Environment Variables for Production

Ensure the following environment variables are set in your production environment:

**Backend:**
- `DATABASE_URL` - Production database URL
- `SECRET_KEY` - Strong secret key for JWT signing
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

**Frontend:**
- `NEXT_PUBLIC_API_BASE_URL` - Production API base URL
- `NEXTAUTH_SECRET` - Secret for NextAuth
- `NEXTAUTH_URL` - Production URL

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify database is running and accessible
   - Check database URL in environment variables
   - Run migrations: `alembic upgrade head`

2. **Authentication Issues**
   - Ensure JWT secret is properly set
   - Verify that Better Auth is properly configured
   - Check that frontend and backend are properly communicating

3. **CORS Issues**
   - Verify CORS settings in the FastAPI backend
   - Ensure frontend URL is properly allowed

### Useful Commands

- **Reset database**: `alembic downgrade base && alembic upgrade head`
- **Check backend API**: `curl http://localhost:7860/health`
- **View all todos for user**: `curl -H "Authorization: Bearer <token>" http://localhost:7860/api/v1/todos`