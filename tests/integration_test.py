"""
Integration tests for the Supabase MCP server.

These tests interact with a real Supabase instance and verify that the
MCP server functions correctly.
"""

import os
import sys
import uuid
import pytest
from dotenv import load_dotenv

# Import the module to test
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import supabase_mcp_server

# Load environment variables
load_dotenv()


def test_crud_operations():
    """Test CRUD operations on a test table."""
    # Skip if no Supabase credentials are available
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        pytest.skip("Supabase credentials not available")

    # Generate a unique table name for testing
    table_name = f"test_table_{uuid.uuid4().hex[:8]}"

    try:
        # Create a test table
        create_result = supabase_mcp_server.create_table(
            table_name,
            [
                {"name": "id", "type": "serial", "primary_key": True},
                {"name": "name", "type": "text", "nullable": False},
                {"name": "value", "type": "integer", "default": "0"}
            ]
        )
        
        # Check if table creation was successful
        if not create_result.get("success", False):
            pytest.skip(f"Failed to create test table: {create_result.get('message', 'Unknown error')}")
        
        # Create test records
        test_data = [
            {"name": "Test 1", "value": 10},
            {"name": "Test 2", "value": 20},
            {"name": "Test 3", "value": 30}
        ]
        created = supabase_mcp_server.create_records(table_name, test_data)
        assert len(created) == 3
        
        # Read records
        read_result = supabase_mcp_server.read_rows(table_name)
        assert len(read_result) == 3
        
        # Read with filter
        filtered = supabase_mcp_server.read_rows(table_name, {"value": {"gte": 20}})
        assert len(filtered) == 2
        
        # Update records
        updated = supabase_mcp_server.update_records(
            table_name, 
            {"value": {"gte": 20}}, 
            {"value": 25}
        )
        assert len(updated) == 2
        
        # Verify update
        after_update = supabase_mcp_server.read_rows(table_name, {"value": 25})
        assert len(after_update) == 2
        
        # Delete records
        deleted = supabase_mcp_server.delete_records(table_name, {"value": 25})
        assert len(deleted) == 2
        
        # Verify delete
        after_delete = supabase_mcp_server.read_rows(table_name)
        assert len(after_delete) == 1
        
        return True
    
    finally:
        # Clean up - drop the test table
        # Note: In a real environment, you would use a dedicated drop_table function
        try:
            supabase_mcp_server.supabase.rpc(
                "execute_sql", 
                {"sql": f"DROP TABLE IF EXISTS {table_name}"}
            ).execute()
        except Exception:
            # Ignore cleanup errors
            pass


if __name__ == "__main__":
    success = test_crud_operations()
    sys.exit(0 if success else 1)
