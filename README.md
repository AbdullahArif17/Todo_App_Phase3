# Multi-User Todo Web Application

A full-stack todo application with user authentication, task management, and responsive UI.

## Features

- User registration and authentication
- Create, read, update, and delete todo tasks
- Mark tasks as complete/incomplete
- User-specific task isolation
- Responsive UI for desktop and mobile

## Tech Stack

- **Frontend**: Next.js 14+, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, SQLModel
- **Database**: PostgreSQL (with Neon Serverless option)
- **Authentication**: JWT-based with secure password hashing

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

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose (optional)

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
```

### Frontend

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
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

## Security

- Passwords are securely hashed using bcrypt
- JWT tokens for authentication with configurable expiration
- Input validation using Pydantic schemas
- SQL injection prevention through SQLModel ORM

## Testing

Coming soon - unit and integration tests for both frontend and backend.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License.