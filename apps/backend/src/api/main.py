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

        # Only add Strict-Transport-Security header if we're not in a proxy environment that might cause redirect loops
        if not request.url.hostname.endswith('.hf.space'):
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
from apps.backend.src.api.v1.chat import router as chat_router
from apps.backend.src.api.v1.conversations import router as conversations_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/api/v1/todos", tags=["Todos"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(conversations_router, prefix="/api/v1", tags=["Conversations"])

from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException

# Middleware to handle proxy headers properly for Hugging Face Spaces
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check for common proxy headers that indicate the original protocol
        forwarded_proto = request.headers.get('x-forwarded-proto', '').lower()
        if forwarded_proto == 'https':
            # Update the request URL scheme to reflect HTTPS
            request.scope['scheme'] = 'https'

        forwarded_host = request.headers.get('x-forwarded-host')
        if forwarded_host:
            # Update the host header if forwarded
            request.scope['headers'] = [
                (k.decode('utf-8') if isinstance(k, bytes) else k, v) if (k.lower() if isinstance(k, str) else k.decode('utf-8').lower()) != b'host'.decode('utf-8') else (b'host'.decode('utf-8'), forwarded_host)
                for k, v in [(h[0], h[1].decode('utf-8')) for h in request.scope.get('headers', [])]
            ]

        response = await call_next(request)
        return response

# Add the proxy headers middleware early in the stack
app.add_middleware(ProxyHeadersMiddleware)

# Add a startup event to log application start
@app.on_event("startup")
def startup_event():
    logger.info(f"Application starting in {settings.ENVIRONMENT} mode")
    logger.info(f"Allowed origins: {settings.allowed_origins_list}")