from fastmcp import FastMCP
from supabase import create_client, Client
import os
from typing import List, Dict, Optional, Any

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create MCP server
mcp = FastMCP(transport='stdio')

@mcp.tool
def read_rows(table_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Read rows from a Supabase table with optional filtering.
    
    Use this tool to query data from any table in your Supabase database.
    You can retrieve all rows or filter results using exact match conditions.
    
    Args:
        table_name (str): Name of the table to query. Must be an existing table in your Supabase project.
        query (Optional[Dict[str, Any]]): Optional filter conditions as key-value pairs.
            Each key should be a column name, and the value is what to match against.
            For example: {"status": "active", "user_id": 123}
            If not provided, all rows will be returned.
    
    Returns:
        List[Dict[str, Any]]: List of matching records as dictionaries.
            Each dictionary contains column names as keys and row values as values.
            Returns an empty list if no matches are found.
    
    Example:
        # Get all users
        read_rows("users")
        
        # Get active users with a specific role
        read_rows("users", {"is_active": True, "role": "admin"})
    """
    if query:
        return supabase.table(table_name).select('*').match(query).execute().data
    return supabase.table(table_name).select('*').execute().data

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
