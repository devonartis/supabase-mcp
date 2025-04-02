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
