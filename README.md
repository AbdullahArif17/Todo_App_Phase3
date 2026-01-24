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

The application follows a monorepo structure with:

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

### Quick Deploy

For production deployment, see the [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) file for complete deployment instructions across various platforms.

### Environment Setup

1. **Copy environment template**:
   ```bash
   cp .env.production .env
   # Update the values in the .env file with your production settings
   # IMPORTANT: Set a strong SECRET_KEY value
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

### Production Setup

1. **Configure environment variables**:
   ```bash
   cp .env.production .env
   # Edit the .env file with your production settings
   # Make sure to set a strong SECRET_KEY
   ```

2. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Verify deployment**:
   ```bash
   # Check if all services are running
   docker-compose -f docker-compose.prod.yml ps

   # Check logs
   docker-compose -f docker-compose.prod.yml logs
   ```

### Manual Production Setup

If you prefer to set up manually:

1. **Build and start services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **Run database migrations**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

3. **Create demo user** (optional):
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python create_demo_user.py
   ```

## Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose (optional for development)

### Development Setup

#### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Start the services
docker-compose up --build
```

The frontend will be available at `http://localhost:3000` and the backend API at `http://localhost:8000`.

#### Option 2: Manual Setup

**Backend:**

```bash
# Navigate to backend
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.api.main:app --reload --port 8000
```

**Frontend:**

```bash
# Navigate to frontend
cd apps/frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

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

## Environment Variables

### Backend

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app_dev
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NODE_ENV=development
```

## Database Migrations

The application uses Alembic for database migrations:

```bash
# From the backend directory
cd apps/backend

# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

## Security Features

- JWT-based authentication with proper token expiration
- Password hashing with bcrypt
- SQL injection prevention through ORM
- XSS protection with proper headers
- Rate limiting to prevent abuse
- CORS configuration for API security
- Input validation and sanitization

## Using the Application

Once both services are running:

1. **Register a new account** by visiting `http://localhost:3000/auth/sign-up`
2. **Log in** with your credentials at `http://localhost:3000/auth/sign-in`
3. **Manage your todos** at `http://localhost:3000/dashboard/todos`

The application provides full CRUD functionality for todo items with authentication and user-specific data isolation. Each user will only see their own tasks, and all security measures are in place to protect user data.

## Production Features

- Docker containerization for consistent deployments
- Nginx reverse proxy for performance and security
- PostgreSQL database for production use
- Redis for caching and session storage
- Health checks and monitoring
- Structured logging
- Environment-based configuration

## Demo Credentials

For testing purposes, a demo user is created during deployment:

- Email: `demo@example.com`
- Password: `demo123`

## Notes:
- The application uses SQLite by default for development (as configured in the backend)
- For production, PostgreSQL is configured in the docker-compose.prod.yml
- All environment variables can be set in `.env` files for both frontend and backend
- The production setup includes security headers, SSL termination (via Nginx), and optimized caching