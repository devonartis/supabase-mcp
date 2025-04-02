"""
Tests for the logging framework.

This module contains tests for the logging functionality.
"""

import os
import sys
import json
import logging
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the module to test
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logger


def test_get_logger():
    """Test that get_logger returns a properly configured logger."""
    test_logger = logger.get_logger("test_logger")
    
    # Check that the logger has the correct name
    assert test_logger.name == "test_logger"
    
    # Check that the logger has at least one handler
    assert len(test_logger.handlers) > 0
    
    # Check that the handler is a StreamHandler
    assert isinstance(test_logger.handlers[0], logging.StreamHandler)
    
    # Check that the formatter is a StructuredLogFormatter
    assert isinstance(test_logger.handlers[0].formatter, logger.StructuredLogFormatter)


def test_structured_log_formatter():
    """Test that the structured log formatter formats logs as expected."""
    formatter = logger.StructuredLogFormatter()
    
    # Create a log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Format the record
    formatted = formatter.format(record)
    
    # Parse the JSON
    log_data = json.loads(formatted)
    
    # Check that the log data has the expected fields
    assert "timestamp" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["name"] == "test_logger"
    assert log_data["message"] == "Test message"


def test_log_with_context():
    """Test logging with additional context."""
    # Create a mock logger
    mock_logger = MagicMock()
    
    # Log with context
    context = {"user_id": 123, "action": "test"}
    logger.log_with_context(mock_logger, "info", "Test message", context)
    
    # Check that the logger was called with the correct arguments
    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    assert args[0] == "Test message"
    assert "extra" in kwargs
    assert kwargs["extra"]["extra"] == context


def test_log_with_exception():
    """Test logging with exception information."""
    # Create a mock logger
    mock_logger = MagicMock()
    
    # Create an exception
    exception = ValueError("Test exception")
    
    # Log with exception
    logger.log_with_context(mock_logger, "error", "Test error", exc_info=exception)
    
    # Check that the logger was called with the correct arguments
    mock_logger.error.assert_called_once()
    args, kwargs = mock_logger.error.call_args
    assert args[0] == "Test error"
    assert "exc_info" in kwargs
    assert kwargs["exc_info"] == exception


def test_convenience_methods():
    """Test the convenience logging methods."""
    # Patch the log_with_context function
    with patch("logger.log_with_context") as mock_log:
        # Test debug
        logger.debug("Debug message", {"level": "debug"})
        mock_log.assert_called_with(logger.mcp_logger, "debug", "Debug message", {"level": "debug"})
        
        # Test info
        logger.info("Info message", {"level": "info"})
        mock_log.assert_called_with(logger.mcp_logger, "info", "Info message", {"level": "info"})
        
        # Test warning
        logger.warning("Warning message", {"level": "warning"})
        mock_log.assert_called_with(logger.mcp_logger, "warning", "Warning message", {"level": "warning"})
        
        # Test error
        exception = ValueError("Test exception")
        logger.error("Error message", {"level": "error"}, exception)
        mock_log.assert_called_with(logger.mcp_logger, "error", "Error message", {"level": "error"}, exception)
        
        # Test critical
        logger.critical("Critical message", {"level": "critical"}, exception)
        mock_log.assert_called_with(logger.mcp_logger, "critical", "Critical message", {"level": "critical"}, exception)


def test_log_output():
    """Test that logs are output as expected."""
    # Capture stdout
    stdout = StringIO()
    
    # Create a handler that writes to our StringIO
    handler = logging.StreamHandler(stdout)
    handler.setFormatter(logger.StructuredLogFormatter())
    
    # Create a logger and add our handler
    test_logger = logging.getLogger("test_output")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)
    
    # Log a message
    test_logger.info("Test output")
    
    # Get the output
    output = stdout.getvalue()
    
    # Check that the output is valid JSON
    log_data = json.loads(output)
    
    # Check that the log data has the expected fields
    assert log_data["level"] == "INFO"
    assert log_data["name"] == "test_output"
    assert log_data["message"] == "Test output"
