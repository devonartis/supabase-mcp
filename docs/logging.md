# Logging System

## Overview

The Supabase MCP Server uses a structured logging system that outputs JSON-formatted logs. This document explains how the logging system works and how to configure it.

## Key Features

- **Structured JSON Logs**: All logs are output in JSON format for easy parsing and analysis
- **Context-Rich Logging**: Additional context can be included with each log entry
- **Exception Tracking**: Full exception details including stack traces are captured
- **Configurable Log Levels**: Log levels can be set via environment variables
- **File Logging Option**: Logs can be written to a file in addition to stderr

## Configuration

The logging system can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Minimum log level to output | `INFO` |
| `LOG_TO_FILE` | Whether to write logs to a file | `false` |
| `LOG_FILE_PATH` | Path to the log file | `supabase_mcp.log` |

### Log Levels

The following log levels are supported, in order of increasing severity:

1. `DEBUG`: Detailed information for debugging purposes
2. `INFO`: General information about system operation
3. `WARNING`: Potential issues that don't prevent normal operation
4. `ERROR`: Errors that prevent specific operations from working
5. `CRITICAL`: Critical errors that may cause the system to fail

## Usage

The logging module provides convenience functions for each log level:

```python
import logger

# Basic logging
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Logging with context
logger.info("User logged in", {"user_id": "123", "ip": "192.168.1.1"})

# Logging exceptions
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.error("Division error", exc_info=e)
```

## Implementation Details

### Output Destination

The logging system writes to `stderr` instead of `stdout`. This is important because:

1. It separates logs from the JSON-RPC communication used by the MCP server
2. It prevents interference with the JSON-RPC protocol
3. It allows logs to be redirected independently of the server's normal output

### Log Format

Each log entry is a JSON object with the following fields:

```json
{
  "timestamp": "2025-04-01T23:45:00.123456+00:00",
  "level": "INFO",
  "name": "supabase_mcp",
  "message": "The log message",
  "extra": {
    "context_field1": "value1",
    "context_field2": "value2"
  }
}
```

When an exception is logged, an additional `exception` field is included:

```json
"exception": {
  "type": "ZeroDivisionError",
  "message": "division by zero",
  "traceback": ["Traceback (most recent call last):", "..."]
}
```

## Best Practices

1. **Use Appropriate Log Levels**: Reserve ERROR and CRITICAL for actual errors
2. **Include Relevant Context**: Add context data to help with debugging
3. **Log Exceptions Properly**: Use the `exc_info` parameter to capture full exception details
4. **Be Concise but Clear**: Log messages should be informative but not overly verbose
5. **Don't Log Sensitive Data**: Avoid logging passwords, API keys, or personal information
