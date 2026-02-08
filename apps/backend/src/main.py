from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from .database import engine
from .api.v1.auth import router as auth_router
from .api.v1.todos import router as todos_router
from .core.config import settings
import logging

# Set up logging
logging.basicConfig(level=settings.LOG_LEVEL.upper())
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Initializing database...")
    # Create database tables
    SQLModel.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully!")

    yield

    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Todo Web Application API",
    description="Secure multi-user todo application with authentication and task management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers to frontend
    expose_headers=["Access-Control-Allow-Origin"]
)

# Include API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/api/v1/todos", tags=["Todos"])

# Include chat API router
from .api.v1.chat import router as chat_router
from .api.v1.conversations import router as conversations_router
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(conversations_router, prefix="/api/v1", tags=["Conversations"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo Web Application API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/api/health")
def api_health_check():
    return {
        "status": "healthy",
        "service": "todo-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Mount static files if needed
# app.mount("/static", StaticFiles(directory="static"), name="static")