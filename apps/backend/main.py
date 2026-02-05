"""
Main application entry point for the Todo AI Chatbot backend
Compatible with Hugging Face Spaces deployment
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.backend.src.api.v1.chat import router as chat_router
from apps.backend.src.api.v1.conversations import router as conversations_router
from apps.backend.src.api.v1.auth import router as auth_router
from apps.backend.src.core.config import settings
from apps.backend.src.database import engine
from apps.backend.src.models.conversation import Conversation
from apps.backend.src.models.message import Message
from apps.backend.src.models.user import User
from sqlmodel import SQLModel


# Create the FastAPI app instance
app = FastAPI(
    title="Todo AI Chatbot API",
    description="Stateless chat API endpoint with AI agent integration for todo management",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add additional origins from environment if needed
    allow_origin_regex=settings.CORS_ORIGIN_REGEX if hasattr(settings, 'CORS_ORIGIN_REGEX') else None,
)

# Include API routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        # Create database tables
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "service": "Todo AI Chatbot Backend",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "service": "Todo AI Chatbot Backend"
    }

# Make sure the app instance is available globally for Hugging Face Spaces
# The variable 'app' is what Hugging Face Spaces will look for
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )