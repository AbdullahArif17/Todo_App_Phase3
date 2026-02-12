"""
Production Configuration for Todo AI Backend
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    Application settings for production deployment
    """
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL") or os.getenv("NEON_DATABASE_URL") or "postgresql://todo_user:todo_password@localhost:5432/todo_db"

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1500"))

    # AI Agent settings
    AI_AGENT_NAME: str = os.getenv("AI_AGENT_NAME", "Todo Assistant")
    AI_AGENT_MODEL: str = os.getenv("AI_AGENT_MODEL", "gpt-4-turbo")
    AI_AGENT_TEMPERATURE: float = float(os.getenv("AI_AGENT_TEMPERATURE", "0.7"))
    AI_AGENT_MAX_TOKENS: int = int(os.getenv("AI_AGENT_MAX_TOKENS", "1500"))
    AI_AGENT_INSTRUCTIONS: str = os.getenv(
        "AI_AGENT_INSTRUCTIONS",
        "You are a helpful todo management assistant that helps users manage their tasks using natural language. "
        "You can help create, update, delete, and list todos. You have access to tools for these operations. "
        "Always respond in a friendly and helpful manner."
    )

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS settings
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://localhost:3000")

    @property
    def allowed_origins_list(self) -> List[str]:
        # Strip whitespace and trailing slashes for exact CORS matching
        return [origin.strip().rstrip("/") for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # in seconds
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "30"))

    # Performance settings
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "5000"))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))

    # MCP Server settings
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "7860"))

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()