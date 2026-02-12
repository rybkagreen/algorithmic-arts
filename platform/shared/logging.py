"""Shared logging configuration for all services."""

import structlog
import sys
from typing import Dict, Any
from contextvars import ContextVar

# Context variable for request_id
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

def add_request_id(logger, method_name, event_dict):
    """Add request_id to log events."""
    try:
        event_dict["request_id"] = request_id_var.get()
    except LookupError:
        # No request_id set, use a default
        event_dict["request_id"] = "unknown"
    return event_dict

def configure_structlog():
    """Configure structlog for all services."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            add_request_id,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None):
    """Get a configured logger instance."""
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()

# Configure logging on import
configure_structlog()