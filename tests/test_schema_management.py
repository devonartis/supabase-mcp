"""
Tests for the schema management tools.

This module contains tests for the schema management functionality,
including creating, altering, and dropping tables.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Import the module to test
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import supabase_mcp_server


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing."""
    with patch('supabase_mcp_server.supabase') as mock_client:
        # Mock the RPC method and its response
        mock_rpc = MagicMock()
        mock_execute = MagicMock()
        
        # Set up the chain of method calls
        mock_client.rpc.return_value = mock_rpc
        mock_rpc.execute.return_value = mock_execute
        mock_execute.data = [{"success": True, "message": "Table created successfully"}]
        
        yield mock_client


def test_create_table(mock_supabase):
    """Test creating a table with the create_table tool."""
    # Define test parameters
    table_name = "test_table"
    columns = [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False},
        {"name": "description", "type": "text", "nullable": True},
        {"name": "created_at", "type": "timestamp", "default": "now()"}
    ]
    
    # Call the function
    result = supabase_mcp_server.create_table(table_name, columns)
    
    # Verify the RPC call was made with the correct parameters
    mock_supabase.rpc.assert_called_once_with(
        "create_table_dynamic",
        {
            "p_table_name": table_name,
            "p_columns": columns
        }
    )
    
    # Verify the result
    assert result == {"success": True, "message": "Table created successfully"}


def test_create_table_with_schema(mock_supabase):
    """Test creating a table in a specific schema."""
    # Define test parameters
    schema_name = "custom_schema"
    table_name = "test_table"
    columns = [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False}
    ]
    
    # Call the function
    supabase_mcp_server.create_table(table_name, columns, schema_name=schema_name)
    
    # Verify the RPC call was made with the correct parameters
    mock_supabase.rpc.assert_called_once_with(
        "create_table_dynamic",
        {
            "p_table_name": table_name,
            "p_columns": columns,
            "p_schema_name": schema_name
        }
    )


def test_create_table_with_error(mock_supabase):
    """Test error handling when creating a table."""
    # Set up the mock to raise an exception
    mock_supabase.rpc.side_effect = Exception("Database error")
    
    # Define test parameters
    table_name = "test_table"
    columns = [
        {"name": "id", "type": "serial", "primary_key": True}
    ]
    
    # Call the function and expect an exception
    with pytest.raises(Exception) as excinfo:
        supabase_mcp_server.create_table(table_name, columns)
    
    # Verify the error message
    assert "Database error" in str(excinfo.value)
