# Schema Management Tools - Developer Guide

## Overview

This guide provides a quick reference for developers working with the schema management tools in the Supabase MCP server. For more detailed documentation, see [schema_management.md](./schema_management.md).

## Available Tools

| Tool | Description | Status |
|------|-------------|--------|
| `create_table` | Create new tables in the database | ✅ Implemented |
| `execute_sql` | Execute arbitrary SQL commands | ✅ Implemented |
| `alter_table` | Modify existing tables | 🔄 Planned |
| `drop_table` | Remove tables from the database | 🔄 Planned |

## Quick Start

### Prerequisites

1. Deploy the required SQL functions to your Supabase database:
   - `sql/create_table_function.sql`
   - `sql/execute_sql_function.sql`

2. Ensure your environment has the required variables:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`

### Creating a Table

```python
from supabase_mcp_server import create_table

result = create_table(
    "users",
    [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "username", "type": "text", "nullable": False},
        {"name": "email", "type": "text", "nullable": False},
        {"name": "created_at", "type": "timestamp", "default": "now()"}
    ]
)

print(result)
```

### Executing SQL

```python
from supabase_mcp_server import execute_sql

result = execute_sql("CREATE INDEX idx_users_email ON users (email)")
print(result)
```

## Error Handling

The schema management tools implement sophisticated error handling to deal with Supabase client quirks. Key points:

1. **Success in Errors**: Sometimes successful operations are reported as errors by the Supabase client
2. **Response Extraction**: We extract success information from error responses
3. **Consistent Return Format**: All tools return a consistent format with `success`, `message`, and operation-specific fields

### Handling Responses

Always check the `success` field in the response:

```python
result = create_table("my_table", [...])
if result["success"]:
    print(f"Table created: {result['table_name']}")
else:
    print(f"Error: {result['message']}")
```

## Common Issues

1. **"Function not found"**: SQL functions not deployed to Supabase
2. **"Permission denied"**: Incorrect or missing service role key
3. **"Table already exists"**: Attempting to create a duplicate table
4. **"Invalid column type"**: Using an unsupported PostgreSQL data type

## Testing

Run the unit tests:
```bash
pytest tests/test_schema_management.py -v
```

Run the integration test:
```bash
python scripts/test_create_table.py
```

## Implementation Details

### Response Format

All schema management tools return responses in this format:

```python
{
    "success": bool,      # Whether the operation succeeded
    "message": str,       # Human-readable message
    # Additional fields specific to the operation
}
```

### Error Handling Flow

1. Try normal execution
2. Catch APIError and extract success data if present
3. Try parsing error message as JSON
4. Look for success keywords in error message
5. Return appropriate success/error response

## Contributing

When adding new schema management tools:

1. Create the PostgreSQL function in `sql/`
2. Implement the MCP tool in `supabase_mcp_server.py`
3. Add unit tests in `tests/test_schema_management.py`
4. Create an integration test script in `scripts/`
5. Update documentation in `docs/schema_management.md`

Follow the existing error handling pattern to ensure consistent behavior.
