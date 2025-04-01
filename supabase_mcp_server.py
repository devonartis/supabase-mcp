from fastmcp import FastMCP
from supabase import create_client, Client
import os
from typing import List, Dict, Optional, Any, Literal

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create MCP server
mcp = FastMCP(transport='stdio')

@mcp.tool
def read_rows(
    table_name: str, 
    query: Optional[Dict[str, Any]] = None,
    select: str = "*",
    order_by: Optional[Dict[str, Literal["asc", "desc"]]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Read rows from a Supabase table with advanced filtering and pagination.
    
    Use this tool to query data from any table in your Supabase database.
    You can retrieve all rows or filter results using exact match conditions,
    order the results, and paginate through large result sets.
    
    Args:
        table_name (str): Name of the table to query. Must be an existing table in your Supabase project.
        query (Optional[Dict[str, Any]]): Optional filter conditions as key-value pairs.
            Each key should be a column name, and the value is what to match against.
            For example: {"status": "active", "user_id": 123}
            If not provided, all rows will be returned (subject to other parameters).
        select (str): Columns to select. Default is "*" for all columns.
            Can be a comma-separated string like "id,name,email" to select specific columns.
        order_by (Optional[Dict[str, Literal["asc", "desc"]]]): Columns to order by and their direction.
            For example: {"created_at": "desc"} or {"name": "asc", "id": "desc"}
        limit (Optional[int]): Maximum number of rows to return. 
            Useful for pagination or limiting large result sets.
        offset (Optional[int]): Number of rows to skip before starting to return rows.
            Used with limit for implementing pagination.
    
    Returns:
        List[Dict[str, Any]]: List of matching records as dictionaries.
            Each dictionary contains column names as keys and row values as values.
            Returns an empty list if no matches are found.
    
    Example:
        # Get all users
        read_rows("users")
        
        # Get active users with a specific role, only select certain fields
        read_rows("users", {"is_active": True, "role": "admin"}, select="id,name,email")
        
        # Get the 10 most recent orders
        read_rows("orders", order_by={"created_at": "desc"}, limit=10)
        
        # Paginate through users, 20 at a time, starting at the 41st user
        read_rows("users", limit=20, offset=40)
    """
    query_builder = supabase.table(table_name).select(select)
    
    # Apply filters if provided
    if query:
        query_builder = query_builder.match(query)
    
    # Apply ordering if provided
    if order_by:
        for column, direction in order_by.items():
            query_builder = query_builder.order(column, ascending=(direction.lower() == "asc"))
    
    # Apply pagination if provided
    if limit is not None:
        query_builder = query_builder.limit(limit)
    
    if offset is not None:
        query_builder = query_builder.offset(offset)
    
    # Execute the query and return the results
    return query_builder.execute().data

@mcp.tool
def create_records(table_name: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create one or more records in a Supabase table.
    
    Use this tool to insert new data into any table in your Supabase database.
    You can insert a single record or multiple records in one operation.
    
    Args:
        table_name (str): Name of the table to insert into. Must be an existing table in your Supabase project.
        records (List[Dict[str, Any]]): List of records to insert.
            Each record should be a dictionary where keys are column names and values are the data to insert.
            For example: [{"name": "John Doe", "email": "john@example.com"}]
            You must provide values for all required columns in the table.
    
    Returns:
        List[Dict[str, Any]]: List of created records as returned by Supabase.
            This typically includes any default values or auto-generated fields (like IDs).
    
    Example:
        # Create a single user
        create_records("users", [{"name": "John Doe", "email": "john@example.com"}])
        
        # Create multiple products at once
        create_records("products", [
            {"name": "Product 1", "price": 29.99, "category": "electronics"},
            {"name": "Product 2", "price": 49.99, "category": "home"}
        ])
    """
    return supabase.table(table_name).insert(records).execute().data

@mcp.tool
def update_records(table_name: str, query: Dict[str, Any], updates: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Update one or more records in a Supabase table.
    
    Use this tool to modify existing data in any table in your Supabase database.
    You can update specific records by providing query conditions.
    
    Args:
        table_name (str): Name of the table to update. Must be an existing table in your Supabase project.
        query (Dict[str, Any]): Conditions to identify which records to update.
            Each key should be a column name, and the value is what to match against.
            For example: {"id": 123} or {"status": "pending"}
            Be careful with broad queries as they might update many records.
        updates (Dict[str, Any]): The changes to apply to matching records.
            Each key should be a column name, and the value is the new value to set.
            For example: {"status": "completed", "updated_at": "2025-03-31"}
    
    Returns:
        List[Dict[str, Any]]: List of updated records with their new values.
            Returns an empty list if no records matched the query conditions.
    
    Example:
        # Update a specific user by ID
        update_records("users", {"id": 123}, {"is_active": False, "last_login": "2025-03-31"})
        
        # Update all products in a category
        update_records("products", {"category": "electronics"}, {"discount": 0.1, "on_sale": True})
    """
    return supabase.table(table_name).update(updates).match(query).execute().data

@mcp.tool
def delete_records(table_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Delete one or more records from a Supabase table.
    
    Use this tool to remove data from any table in your Supabase database.
    You must provide query conditions to identify which records to delete.
    
    Args:
        table_name (str): Name of the table to delete from. Must be an existing table in your Supabase project.
        query (Dict[str, Any]): Conditions to identify which records to delete.
            Each key should be a column name, and the value is what to match against.
            For example: {"id": 123} or {"status": "cancelled"}
            IMPORTANT: Be very careful with broad queries as they might delete many records.
            Always use specific conditions when possible.
    
    Returns:
        List[Dict[str, Any]]: List of deleted records.
            This contains the data that was deleted, which can be useful for confirmation or undo operations.
            Returns an empty list if no records matched the query conditions.
    
    Example:
        # Delete a specific user by ID
        delete_records("users", {"id": 123})
        
        # Delete all cancelled orders older than a certain date
        delete_records("orders", {"status": "cancelled", "created_at": {"lt": "2025-01-01"}})
    """
    return supabase.table(table_name).delete().match(query).execute().data

if __name__ == '__main__':
    mcp.run()
