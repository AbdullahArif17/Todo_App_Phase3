from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.gzip import GZipMiddleware
from src.core.config import settings
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Todo Web Application API",
    description="Secure multi-user todo application with authentication and authorization",
    version="1.0.0",
    debug=settings.DEBUG
)

# Security middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        return response

# Add security and performance middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - allow specific origins based on environment
allowed_origins = settings.allowed_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers to frontend
    expose_headers=["Access-Control-Allow-Origin"]
)

# Trusted host middleware to prevent HTTP Host header attacks
# Allow all hosts in development, restrict in production
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"] if settings.DEBUG else ["todo-app.com", "www.todo-app.com", "abdullah017-todoapp-phase2.hf.space", "abdullah017-todoapp-phase2.hf.space."])

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
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }

# Import and include routers
from src.api.v1.auth import router as auth_router
from src.api.v1.todos import router as todos_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/api/v1/todos", tags=["Todos"])

# Add a startup event to log application start
@app.on_event("startup")
def startup_event():
    logger.info(f"Application starting in {settings.ENVIRONMENT} mode")
    logger.info(f"Allowed origins: {settings.allowed_origins_list}")