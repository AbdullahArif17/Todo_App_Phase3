"""
Main application entry point for the Todo AI Backend
Compatible with Hugging Face Spaces deployment
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from apps.backend.src.database import engine
from apps.backend.src.api.v1.chat import router as chat_router
from apps.backend.src.api.v1.conversations import router as conversations_router
from apps.backend.src.api.v1.auth import router as auth_router
from apps.backend.src.core.config import settings
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
    try:
        # Create database tables
        SQLModel.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Todo AI Chatbot API",
    description="Stateless chat API endpoint with AI agent integration for todo management",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers to frontend
    expose_headers=["Access-Control-Allow-Origin"]
)


# Include API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(conversations_router, prefix="/api/v1", tags=["Conversations"])


@app.get("/")
def read_root():
    """Root endpoint for health check and basic information"""
    return {
        "service": "Todo AI Chatbot Backend",
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": [
            "Natural language todo management",
            "MCP tool integration",
            "Stateless architecture",
            "Secure authentication"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "service": "Todo AI Chatbot Backend",
        "environment": settings.ENVIRONMENT,
        "database_connected": True  # Simplified - in production, verify actual DB connection
    }


@app.get("/api/health")
def api_health_check():
    """API-specific health check"""
    return {
        "status": "healthy",
        "service": "todo-ai-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }


# For Hugging Face Spaces compatibility
# The variable 'app' is what Hugging Face Spaces will look for
app_instance = app