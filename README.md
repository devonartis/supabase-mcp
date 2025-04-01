# Supabase MCP Server

A Model Context Protocol (MCP) server for interacting with Supabase databases. This server provides tools for performing CRUD operations on Supabase tables through a standardized interface that can be used by LLMs and other MCP clients.

## Features

- **Read Operations**: Query and filter data from any table
- **Create Operations**: Insert new records into tables
- **Update Operations**: Modify existing records with flexible querying
- **Delete Operations**: Remove records from tables with safety controls

## Installation

### Prerequisites

- Python 3.9+
- A Supabase project with service role key

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
   ```

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

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Project Structure

- `supabase_mcp_server.py`: Main server implementation
- `tests/`: Test suite for the server
  - `test_supabase_mcp_server.py`: Unit tests
  - `integration_test.py`: Integration tests

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
