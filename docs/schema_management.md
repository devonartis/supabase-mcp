# Schema Management in Supabase MCP

This document explains how to use the schema management tools in the Supabase MCP server, including how to set up the required SQL functions in your Supabase database.

## Table Creation

The `create_table` tool allows you to programmatically create new tables in your Supabase database. This is useful for:

- Setting up initial database schema
- Creating temporary tables for data processing
- Extending applications with new features that require additional tables

### Prerequisites

Before you can use the `create_table` tool, you need to deploy the `create_table_dynamic` SQL function to your Supabase database.

#### Deploying the SQL Function

1. Log in to your [Supabase Dashboard](https://app.supabase.com/)
2. Navigate to your project
3. Go to the SQL Editor
4. Create a new query
5. Copy and paste the contents of the `sql/create_table_function.sql` file
6. Run the query

Alternatively, you can use the Supabase CLI to deploy the function:

```bash
supabase db push --db-url <your-db-url> sql/create_table_function.sql
```

### Usage

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
# {
#     "success": true,
#     "message": "Table created successfully",
#     "table_name": "public.products",
#     "sql": "CREATE TABLE public.products (id serial NOT NULL, name text NOT NULL, description text, price numeric(10,2) DEFAULT 0, created_at timestamp DEFAULT now(), PRIMARY KEY (id))"
# }
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
