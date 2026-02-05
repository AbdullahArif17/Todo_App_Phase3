"""
Audit Logging for MCP Server Security Monitoring
Provides security-focused logging for all tool access attempts
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import uuid


# Create logger for MCP security events
mcp_security_logger = logging.getLogger('mcp.security')
mcp_security_logger.setLevel(logging.INFO)

# Create file handler for security events
security_handler = logging.FileHandler('mcp_security.log')
security_handler.setLevel(logging.INFO)

# Create formatter for security events
security_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
security_handler.setFormatter(security_formatter)

# Add handler to logger
mcp_security_logger.addHandler(security_handler)
mcp_security_logger.propagate = False  # Prevent duplicate logs


def log_tool_access_attempt(
    user_id: str,
    tool_name: str,
    ip_address: Optional[str] = None,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an MCP tool access attempt for security monitoring.

    Args:
        user_id: The ID of the user attempting to access the tool
        tool_name: The name of the tool being accessed
        ip_address: The IP address of the request (optional)
        success: Whether the access attempt was successful
        details: Additional details about the access attempt (optional)
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        # Log invalid user_id format attempts as potential security issues
        mcp_security_logger.warning(
            f"SECURITY: Invalid user_id format in tool access attempt - "
            f"tool={tool_name}, user_id={user_id}, ip={ip_address}"
        )
        return

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "mcp_tool_access",
        "user_id": str(user_uuid),
        "tool_name": tool_name,
        "ip_address": ip_address,
        "success": success,
        "details": details
    }

    if success:
        mcp_security_logger.info(f"MCP_TOOL_ACCESS_SUCCESS: {json.dumps(log_data)}")
    else:
        mcp_security_logger.warning(f"MCP_TOOL_ACCESS_FAILURE: {json.dumps(log_data)}")


def log_security_violation(
    user_id: str,
    tool_name: str,
    violation_type: str,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log a security violation for MCP tool access.

    Args:
        user_id: The ID of the user involved in the violation
        tool_name: The name of the tool involved
        violation_type: Type of security violation
        ip_address: The IP address of the request (optional)
        details: Additional details about the violation (optional)
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        user_uuid = "INVALID_FORMAT"

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "security_violation",
        "violation_type": violation_type,
        "user_id": str(user_uuid) if isinstance(user_uuid, uuid.UUID) else user_uuid,
        "tool_name": tool_name,
        "ip_address": ip_address,
        "details": details
    }

    mcp_security_logger.error(f"SECURITY_VIOLATION: {json.dumps(log_data)}")


def log_rate_limit_event(
    user_id: str,
    tool_name: str,
    ip_address: Optional[str] = None,
    limit_type: str = "unknown"
) -> None:
    """
    Log a rate limiting event for MCP tool access.

    Args:
        user_id: The ID of the user who hit the rate limit
        tool_name: The name of the tool that was rate limited
        ip_address: The IP address of the request (optional)
        limit_type: Type of rate limit that was hit
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        user_uuid = "INVALID_FORMAT"

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "rate_limit_hit",
        "limit_type": limit_type,
        "user_id": str(user_uuid) if isinstance(user_uuid, uuid.UUID) else user_uuid,
        "tool_name": tool_name,
        "ip_address": ip_address
    }

    mcp_security_logger.warning(f"RATE_LIMIT_HIT: {json.dumps(log_data)}")


def log_input_validation_failure(
    user_id: str,
    tool_name: str,
    parameter_name: str,
    received_value: Any,
    ip_address: Optional[str] = None
) -> None:
    """
    Log an input validation failure for MCP tool access.

    Args:
        user_id: The ID of the user whose input failed validation
        tool_name: The name of the tool with validation failure
        parameter_name: The name of the parameter that failed validation
        received_value: The value that failed validation
        ip_address: The IP address of the request (optional)
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        user_uuid = "INVALID_FORMAT"

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "input_validation_failure",
        "user_id": str(user_uuid) if isinstance(user_uuid, uuid.UUID) else user_uuid,
        "tool_name": tool_name,
        "parameter_name": parameter_name,
        "received_value": str(received_value),
        "ip_address": ip_address
    }

    mcp_security_logger.warning(f"INPUT_VALIDATION_FAILURE: {json.dumps(log_data)}")