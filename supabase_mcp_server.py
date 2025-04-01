from fastmcp import FastMCP
from supabase import create_client, Client
import os
from typing import List, Dict, Optional

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create MCP server
mcp = FastMCP(transport='stdio')

@mcp.tool
def read_rows(table_name: str, query: Optional[Dict] = None) -> List[Dict]:
    """
    Read rows from a Supabase table.

    Args:
        table_name (str): Name of the table to query.
        query (Optional[Dict]): Optional query parameters to filter results.

    Returns:
        List[Dict]: List of rows matching the query.
    """
    if query:
        return supabase.table(table_name).select('*').match(query).execute().data
    return supabase.table(table_name).select('*').execute().data

@mcp.tool
def create_records(table_name: str, records: List[Dict]) -> List[Dict]:
    """
    Create one or more records in a Supabase table.

    Args:
        table_name (str): Name of the table to insert into.
        records (List[Dict]): List of records to insert.

    Returns:
        List[Dict]: List of created records.
    """
    return supabase.table(table_name).insert(records).execute().data

@mcp.tool
def update_records(table_name: str, query: Dict, updates: Dict) -> List[Dict]:
    """
    Update one or more records in a Supabase table.

    Args:
        table_name (str): Name of the table to update.
        query (Dict): Query to identify records to update.
        updates (Dict): Fields to update and their new values.

    Returns:
        List[Dict]: List of updated records.
    """
    return supabase.table(table_name).update(updates).match(query).execute().data

@mcp.tool
def delete_records(table_name: str, query: Dict) -> List[Dict]:
    """
    Delete one or more records from a Supabase table.

    Args:
        table_name (str): Name of the table to delete from.
        query (Dict): Query to identify records to delete.

    Returns:
        List[Dict]: List of deleted records.
    """
    return supabase.table(table_name).delete().match(query).execute().data

if __name__ == '__main__':
    mcp.run()
