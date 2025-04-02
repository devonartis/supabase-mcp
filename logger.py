"""
Logging module for the Supabase MCP server.

This module provides a configurable logging framework with structured logging
and proper error reporting.
"""

import logging
import json
import sys
import os
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union

# Configure default log level from environment variable or default to INFO
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class StructuredLogFormatter(logging.Formatter):
    """
    Custom formatter for structured logging with JSON output.
    
    This formatter outputs logs in JSON format with consistent fields,
    making it easier to parse and analyze logs in production environments.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.
        
        Args:
            record: The log record to format
            
        Returns:
            A JSON string representation of the log record
        """
        # Basic log data
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        # Add extra fields from the record
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger with the specified name and level.
    
    Args:
        name: The name of the logger
        level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              If not provided, uses the default log level
              
    Returns:
        A configured logger instance
    """
    # Get or create a logger
    logger = logging.getLogger(name)
    
    # Set the log level
    log_level = LOG_LEVELS.get(
        level.upper() if level else DEFAULT_LOG_LEVEL, 
        logging.INFO
    )
    logger.setLevel(log_level)
    
    # Only add handlers if they don't exist yet
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(console_handler)
    
    return logger


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Union[bool, Exception]] = None
) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: The logger to use
        level: The log level (debug, info, warning, error, critical)
        message: The log message
        context: Additional context to include in the log
        exc_info: Exception information to include
    """
    log_method = getattr(logger, level.lower(), logger.info)
    
    # Create a new record with extra context
    extra = {"extra": context or {}}
    
    # Log with context and optional exception info
    log_method(message, extra=extra, exc_info=exc_info)


# Create a default logger for the MCP server
mcp_logger = get_logger("supabase_mcp")


# Convenience methods for logging with context
def debug(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Log a debug message with context."""
    log_with_context(mcp_logger, "debug", message, context)


def info(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an info message with context."""
    log_with_context(mcp_logger, "info", message, context)


def warning(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Log a warning message with context."""
    log_with_context(mcp_logger, "warning", message, context)


def error(
    message: str, 
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Union[bool, Exception]] = None
) -> None:
    """Log an error message with context and optional exception info."""
    log_with_context(mcp_logger, "error", message, context, exc_info)


def critical(
    message: str, 
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Union[bool, Exception]] = None
) -> None:
    """Log a critical message with context and optional exception info."""
    log_with_context(mcp_logger, "critical", message, context, exc_info)
