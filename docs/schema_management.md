# Schema Management in Supabase MCP

This document explains how to use the schema management tools in the Supabase MCP server, including how to set up the required SQL functions in your Supabase database.

## ⚠️ IMPORTANT: Required Setup

**The `create_table` tool will NOT work until you deploy the required SQL function to your Supabase database.**

This is a one-time setup step that must be completed before using any schema management tools.

## Architecture Overview

The schema management tools use a two-step approach:

1. **MCP Tool**: The Python function in the MCP server that provides a clean interface for AI assistants
2. **PostgreSQL Function**: A function that runs inside the Supabase database to perform the actual schema changes

This architecture is necessary because:
- The Supabase client doesn't allow executing arbitrary SQL statements like `CREATE TABLE` directly
- PostgreSQL functions can run with elevated permissions inside the database
- It provides better error handling and security controls

## Table Creation

The `create_table` tool allows you to programmatically create new tables in your Supabase database. This is useful for:

- Setting up initial database schema
- Creating temporary tables for data processing
- Extending applications with new features that require additional tables

### Required Setup: Deploying the SQL Function

**The `create_table` tool will NOT work until you complete these steps:**

1. **Access Supabase SQL Editor**
   - Log in to your [Supabase Dashboard](https://app.supabase.com/)
   - Navigate to your project
   - Click on "SQL Editor" in the left sidebar

2. **Create a New Query**
   - Click the "New Query" button
   - Give it a name like "Create Table Function"

3. **Copy the SQL Function Code**
   - Open the file `sql/create_table_function.sql` in your project
   - Copy the entire contents of this file

4. **Deploy the Function**
   - Paste the SQL code into the SQL Editor
   - Click the "Run" button
   - Verify that the query executes successfully with no errors

5. **Verify the Function Exists**
   - Go to "Database" → "Functions" in the Supabase Dashboard
   - Confirm that `create_table_dynamic` appears in the list of functions

If you encounter any errors during this process, check the error message for details. Common issues include:
- Syntax errors in the SQL function
- Permission issues (make sure you're using the service role key)
- Conflicts with existing functions

### Alternative: Using Supabase CLI

If you have the Supabase CLI installed, you can deploy the function with:

```bash
# Make sure you're in the project root directory
supabase db push --db-url <your-db-url> sql/create_table_function.sql
```

### How It Works

When you call the `create_table` MCP tool:

1. The MCP server formats your parameters into the format expected by the PostgreSQL function
2. It calls the `create_table_dynamic` function via RPC (Remote Procedure Call)
3. The PostgreSQL function generates and executes the `CREATE TABLE` SQL statement
4. The result is returned to the MCP server and then to the caller

This indirect approach allows us to perform operations that aren't directly supported by the Supabase client while maintaining proper security controls.

### Usage

**⚠️ Remember: The `create_table` tool will NOT work until you deploy the SQL function as described above.**

Once the SQL function is deployed, you can use the `create_table` tool in your MCP client:

```python
# Example: Creating a users table
create_table(
    "users",
    [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "username", "type": "text", "nullable": False},
        {"name": "email", "type": "text", "nullable": False},
        {"name": "created_at", "type": "timestamp", "default": "now()"}
    ]
)
```

### Parameters

- `table_name` (str): Name of the table to create
- `columns` (List[Dict]): List of column definitions, each with:
  - `name` (str): Column name
  - `type` (str): PostgreSQL data type
  - `nullable` (bool, optional): Whether the column can be NULL
  - `default` (str, optional): Default value expression
  - `primary_key` (bool, optional): Whether this column is part of the primary key
- `schema_name` (str, optional): Name of the schema to create the table in (default: "public")

### Response

The tool returns a dictionary with:

- `success` (bool): Whether the operation was successful
- `message` (str): A message describing the result
- `table_name` (str): The fully qualified table name (if successful)
- `sql` (str): The SQL statement that was executed

### Example

```python
result = create_table(
    "products",
    [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False},
        {"name": "description", "type": "text"},
        {"name": "price", "type": "numeric(10,2)", "default": "0"},
        {"name": "created_at", "type": "timestamp", "default": "now()"}
    ]
)

# Result:
```python
{
    "success": True,
    "message": "Table created successfully",
    "table_name": "public.products",
    "sql": "CREATE TABLE public.products (id serial NOT NULL, name text NOT NULL, description text, price numeric(10,2) DEFAULT 0, created_at timestamp DEFAULT now(), PRIMARY KEY (id))"
}
```

## Error Handling in Schema Management Tools

### Understanding Supabase Client Response Handling

The schema management tools in this MCP server implement a sophisticated error handling approach to deal with a specific quirk in the Supabase Python client. This section explains the issue and our solution in detail.

#### The Problem

When using the Supabase Python client to call RPC functions that return custom JSON responses, the client may incorrectly interpret successful responses as errors. This happens because:

1. The PostgreSQL functions return custom JSON objects with a `success` field
2. The Supabase client expects a specific response format
3. When the response doesn't match the expected format, the client raises an `APIError`
4. However, the operation itself (creating a table, executing SQL) actually succeeds in the database

This creates a confusing situation where successful operations appear to fail from the client's perspective.

#### Our Solution

We've implemented a multi-layered error handling approach that:

1. **Attempts normal execution first**
2. **Catches and analyzes `APIError` exceptions**
3. **Extracts success information from error responses**
4. **Returns consistent success/failure data to callers**

The error handling logic follows this sequence:

1. **Primary Execution Path**: Try to execute the RPC call normally
   - If successful and the response indicates success, return the success data
   - If successful but the response indicates failure, return the failure data

2. **APIError Handling Path**: If an `APIError` is raised
   - Check if the error data is a dictionary with `success: true`
   - If so, treat it as a successful response
   - If not, try to parse the error data as JSON
   - If parsing succeeds and the result has `success: true`, treat it as successful
   - If parsing fails, try to extract JSON-like data using regex
   - If all extraction attempts fail, check for success keywords in the error message
   - If all approaches fail, return a proper error response

3. **General Exception Handling**: Catch any other exceptions
   - Log the exception details
   - Return a proper error response

This approach ensures that operations that actually succeed in the database are correctly reported as successful to the caller, regardless of how the Supabase client interprets the response.

### Debugging Response Issues

If you're developing new schema management tools or modifying existing ones, you may need to debug response handling issues. Here are some tips:

1. **Examine Raw Error Data**: When an `APIError` occurs, examine `e.args[0]` to see the raw error data
2. **Check Database Directly**: Verify in the Supabase Dashboard if the operation actually succeeded
3. **Add Temporary Logging**: Add temporary logging to print the raw response data
4. **Test with Different Response Formats**: Test how the client handles different response formats

## Execute SQL Function

The `execute_sql` tool allows you to run arbitrary SQL commands in your Supabase database. This is useful for:

- Running DDL statements (CREATE INDEX, ALTER TABLE, etc.)
- Executing complex queries
- Performing database maintenance tasks
- Testing SQL commands

### Required Setup: Deploying the SQL Function

**The `execute_sql` tool will NOT work until you complete these steps:**

1. **Access Supabase SQL Editor**
   - Log in to your [Supabase Dashboard](https://app.supabase.com/)
   - Navigate to your project
   - Click on "SQL Editor" in the left sidebar

2. **Create a New Query**
   - Click the "New Query" button
   - Give it a name like "Execute SQL Function"

3. **Copy the SQL Function Code**
   - Open the file `sql/execute_sql_function.sql` in your project
   - Copy the entire contents of this file

4. **Deploy the Function**
   - Paste the SQL code into the SQL Editor
   - Click the "Run" button
   - Verify that the query executes successfully with no errors

5. **Verify the Function Exists**
   - Go to "Database" → "Functions" in the Supabase Dashboard
   - Confirm that `execute_sql` appears in the list of functions

### Usage

Once the SQL function is deployed, you can use the `execute_sql` tool in your MCP client:

```python
# Example: Creating an index
result = execute_sql("CREATE INDEX idx_users_email ON users (email)")

# Example: Dropping a table
result = execute_sql("DROP TABLE IF EXISTS temporary_data")

# Example: Altering a table
result = execute_sql("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
```

### Parameters

- `sql` (str): The SQL statement to execute

### Response

The tool returns a dictionary with:

- `success` (bool): Whether the operation was successful
- `message` (str): A message describing the result
- `sql` (str): The SQL statement that was executed

### Example

```python
result = execute_sql("CREATE INDEX idx_products_name ON products (name)")

# Result:
{
    "success": True,
    "message": "SQL executed successfully",
    "sql": "CREATE INDEX idx_products_name ON products (name)"
}
```

### Security Considerations

- The `execute_sql` tool is very powerful and should be used with extreme caution
- It can execute ANY SQL command, including destructive operations like DROP TABLE
- Always validate and sanitize SQL commands before execution
- Consider implementing additional validation in your application
- Use more specific tools (like `create_table`) when possible instead of raw SQL

## Testing Schema Management Tools

We've developed comprehensive tests for the schema management tools to ensure they work correctly:

1. **Unit Tests**: Located in `tests/test_schema_management.py`
   - Test normal operation with mock responses
   - Test error handling with various error scenarios
   - Test edge cases and special response formats

2. **Integration Test Script**: Located in `scripts/test_create_table.py`
   - Tests actual table creation in a live Supabase database
   - Verifies that tables can be created and used
   - Includes cleanup to remove test tables
   - Demonstrates proper error handling

### Running the Tests

To run the unit tests:

```bash
pytest tests/test_schema_management.py -v
```

To run the integration test script:

```bash
python scripts/test_create_table.py
```

### Test Design

The tests are designed to verify:

1. **Functionality**: Do the tools perform their intended operations?
2. **Error Handling**: Do the tools properly handle various error scenarios?
3. **Edge Cases**: Do the tools work with unusual inputs and response formats?
4. **Integration**: Do the tools work correctly with a real Supabase database?

## Common Issues and Solutions

### Table Creation Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| "Table already exists" | A table with the same name already exists | Use a different table name or drop the existing table first |
| "Invalid column type" | The specified column type is not valid in PostgreSQL | Check PostgreSQL documentation for valid data types |
| "Permission denied" | The service role key doesn't have sufficient permissions | Ensure you're using the correct service role key |
| "Function not found" | The SQL function hasn't been deployed | Follow the setup instructions to deploy the function |

### Execute SQL Issues

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| "Syntax error" | The SQL statement has syntax errors | Check the SQL syntax and fix any errors |
| "Relation does not exist" | The table or view doesn't exist | Verify the table name and schema |
| "Permission denied" | The service role key doesn't have sufficient permissions | Ensure you're using the correct service role key |
| "Function not found" | The SQL function hasn't been deployed | Follow the setup instructions to deploy the function |

## Best Practices

1. **Use Descriptive Table Names**: Choose clear, descriptive names for tables and columns
2. **Include Primary Keys**: Always define a primary key for each table
3. **Use Appropriate Data Types**: Choose the most appropriate data type for each column
4. **Add Constraints**: Use NOT NULL, UNIQUE, and other constraints to enforce data integrity
5. **Document Your Schema**: Keep documentation of your database schema up to date
6. **Test Before Production**: Test schema changes in a development environment first
7. **Back Up Before Changes**: Always back up your database before making schema changes
8. **Use Transactions**: Wrap multiple schema changes in a transaction when possible
9. **Implement Row Level Security**: Add RLS policies to protect your data
10. **Monitor Performance**: Monitor query performance after schema changes

## Future Enhancements

We plan to add more schema management tools in the future:

- `alter_table`: Modify existing tables (add/drop columns, change column types, etc.)
- `drop_table`: Remove tables from the database
- `create_index`: Create indexes on tables
- `create_view`: Create database views
- `create_function`: Create custom PostgreSQL functions

## Security Considerations

- The `create_table` tool requires the service role key, which has elevated privileges
- Table creation is a powerful operation that should be used with caution
- Consider using Row Level Security (RLS) policies on any tables you create
- The SQL function is created with `SECURITY DEFINER` to ensure it runs with the appropriate permissions

## Troubleshooting

If you encounter errors when using the `create_table` tool, check the following:

1. Ensure the `create_table_dynamic` SQL function is deployed to your Supabase database
2. Verify that your service role key has the necessary permissions
3. Check that the column types are valid PostgreSQL data types
4. Ensure the table name follows PostgreSQL naming conventions
5. Check the logs for detailed error messages
