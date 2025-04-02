# Supabase MCP Server

A Model Context Protocol (MCP) server for interacting with Supabase databases. This server provides tools for performing CRUD operations and schema management on Supabase tables through a standardized interface that can be used by LLMs and other MCP clients.

## Features

- **Read Operations**: Query and filter data from any table
- **Create Operations**: Insert new records into tables
- **Update Operations**: Modify existing records with flexible querying
- **Delete Operations**: Remove records from tables with safety controls
- **Schema Management**: Create tables and execute SQL commands programmatically
- **Structured Logging**: Comprehensive logging with JSON formatting and context

## Installation

### Prerequisites

- Python 3.9+
- A Supabase project with service role key
- python-dotenv (for environment variable management)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/supabase-mcp.git
   cd supabase-mcp
   ```

2. Install dependencies using UV:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Create a `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   LOG_LEVEL=INFO  # Optional: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   ```
   
   The server uses python-dotenv to automatically load these environment variables from the .env file.

## Usage

### Running the Server

Start the MCP server:

```bash
python supabase_mcp_server.py
```

The server uses stdio transport, so it can be integrated with any MCP client that supports this protocol.

### Available Tools

#### read_rows

Query and filter data from a Supabase table with advanced filtering and pagination.

**Parameters:**
- `table_name` (string): Name of the table to query
- `query` (optional object): Filter conditions for the query
- `select` (string): Columns to select (default: "*" for all columns)
- `order_by` (optional object): Columns to order by and their direction ("asc" or "desc")
- `limit` (optional number): Maximum number of rows to return
- `offset` (optional number): Number of rows to skip (for pagination)

**Example:**
```python
# Read all rows from the 'users' table
read_rows("users")

# Read rows with specific conditions
read_rows("users", {"is_active": true, "role": "admin"})

# Select specific columns
read_rows("users", select="id,name,email")

# Get the 10 most recent orders
read_rows("orders", order_by={"created_at": "desc"}, limit=10)

# Paginate through users, 20 at a time, starting at the 41st user
read_rows("users", limit=20, offset=40)
```

#### create_records

Insert one or more records into a Supabase table.

**Parameters:**
- `table_name` (string): Name of the table to insert into
- `records` (array of objects): Records to insert

**Example:**
```python
# Create a single record
create_records("users", [{"name": "John Doe", "email": "john@example.com"}])

# Create multiple records
create_records("products", [
  {"name": "Product 1", "price": 29.99},
  {"name": "Product 2", "price": 49.99}
])
```

#### update_records

Update records in a Supabase table based on query conditions.

**Parameters:**
- `table_name` (string): Name of the table to update
- `query` (object): Conditions to identify records to update
- `updates` (object): Fields to update and their new values

**Example:**
```python
# Update a specific record
update_records("users", {"id": 123}, {"is_active": false})

# Update multiple records matching a condition
update_records("products", {"category": "electronics"}, {"discount": 0.1})
```

#### delete_records

Delete records from a Supabase table based on query conditions.

**Parameters:**
- `table_name` (string): Name of the table to delete from
- `query` (object): Conditions to identify records to delete

**Example:**
```python
# Delete a specific record
delete_records("users", {"id": 123})

# Delete multiple records matching a condition
delete_records("orders", {"status": "cancelled"})
```

#### create_table

Create a new table in the Supabase database with specified columns.

**Parameters:**
- `table_name` (string): Name of the table to create
- `columns` (array of objects): Column definitions with name, type, and constraints
- `schema_name` (optional string): Schema to create the table in (default: "public")

Each column object can include:
- `name` (string): Column name
- `type` (string): PostgreSQL data type
- `nullable` (optional boolean): Whether the column can contain NULL values
- `unique` (optional boolean): Whether values must be unique
- `primary` (optional boolean): Whether this is a primary key
- `default` (optional string): Default value expression

**Example:**
```python
# Create a simple users table
create_table(
    "users",
    [
        {"name": "id", "type": "serial", "primary": true},
        {"name": "username", "type": "text", "unique": true, "nullable": false},
        {"name": "email", "type": "text", "unique": true, "nullable": false},
        {"name": "created_at", "type": "timestamp", "default": "now()"}
    ]
)
```

#### execute_sql

Execute arbitrary SQL commands in the Supabase database.

**Parameters:**
- `sql` (string): SQL command to execute

**Example:**
```python
# Create an index
execute_sql("CREATE INDEX idx_users_email ON users(email)")

# Add a check constraint
execute_sql("ALTER TABLE products ADD CONSTRAINT positive_price CHECK (price > 0)")
```

## Development

### Logging

The server includes a comprehensive logging framework that provides structured logging with JSON output. Logs include timestamps, log levels, and contextual information about operations.

#### Log Levels

You can configure the log level by setting the `LOG_LEVEL` environment variable:

```
LOG_LEVEL=DEBUG  # For detailed debugging information
LOG_LEVEL=INFO   # For general operational information (default)
LOG_LEVEL=WARNING  # For warning conditions
LOG_LEVEL=ERROR  # For error conditions
LOG_LEVEL=CRITICAL  # For critical errors
```

#### Log Format

Logs are output in JSON format with the following structure:

```json
{
  "timestamp": "2025-04-01T21:00:00.000000",
  "level": "INFO",
  "name": "supabase_mcp",
  "message": "Reading rows from table 'users'",
  "extra": {
    "table": "users",
    "query": {"is_active": true}
  }
}
```

This structured format makes it easy to parse and analyze logs in production environments.

### Running Tests

```bash
uv run pytest tests/
```

### Project Structure

- `supabase_mcp_server.py`: Main server implementation
- `logger.py`: Logging framework
- `tests/`: Test suite for the server
  - `test_supabase_mcp_server.py`: Unit tests for the MCP server
  - `test_logger.py`: Unit tests for the logging framework
  - `integration_test.py`: Integration tests

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
