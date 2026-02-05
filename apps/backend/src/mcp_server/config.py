"""
Configuration for MCP Server
Handles settings and configuration for the MCP tools and server
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class MCPConfig(BaseSettings):
    """
    Configuration settings for the MCP Server
    """
    # Server settings
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8001"))

    # Database settings (reuse from existing app)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://todo_user:todo_password@localhost:5432/todo_db")

    # AI service settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Rate limiting
    MCP_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("MCP_RATE_LIMIT_PER_MINUTE", "30"))

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"


# Global configuration instance
mcp_config = MCPConfig()