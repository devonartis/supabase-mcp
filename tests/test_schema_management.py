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
from postgrest.exceptions import APIError


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
    """Test creating a table with a custom schema."""
    # Define test parameters
    table_name = "test_table"
    schema_name = "custom_schema"
    columns = [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False}
    ]
    
    # Call the function
    result = supabase_mcp_server.create_table(table_name, columns, schema_name)
    
    # Verify the RPC call was made with the correct parameters
    mock_supabase.rpc.assert_called_once_with(
        "create_table_dynamic",
        {
            "p_table_name": table_name,
            "p_columns": columns,
            "p_schema_name": schema_name
        }
    )
    
    # Verify the result
    assert result == {"success": True, "message": "Table created successfully"}


def test_create_table_with_error(mock_supabase):
    """Test error handling when creating a table."""
    # Define test parameters
    table_name = "test_table"
    columns = [{"name": "id", "type": "invalid_type"}]
    
    # Mock an error response
    mock_rpc = MagicMock()
    mock_supabase.rpc.return_value = mock_rpc
    mock_rpc.execute.side_effect = Exception("Database error")
    
    # Call the function
    result = supabase_mcp_server.create_table(table_name, columns)
    
    # Verify the result contains the error
    assert result["success"] is False
    assert "Database error" in result["message"]


def test_create_table_with_api_error_success(mock_supabase):
    """Test handling APIError that actually contains a success response."""
    # Define test parameters
    table_name = "test_table"
    columns = [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False}
    ]
    
    # Mock an APIError with a success response
    success_response = {
        "sql": f"CREATE TABLE public.{table_name} (id serial, name text NOT NULL, PRIMARY KEY (id))",
        "message": "Table created successfully",
        "success": True,
        "table_name": f"public.{table_name}"
    }
    mock_rpc = MagicMock()
    mock_supabase.rpc.return_value = mock_rpc
    mock_rpc.execute.side_effect = APIError(success_response)
    
    # Call the function
    result = supabase_mcp_server.create_table(table_name, columns)
    
    # Verify the result is treated as a success
    assert result["success"] is True
    assert result["message"] == "Table created successfully"
    assert result["table_name"] == f"public.{table_name}"


def test_create_table_with_api_error_string(mock_supabase):
    """Test handling APIError with a string that contains a success response."""
    # Define test parameters
    table_name = "test_table"
    columns = [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False}
    ]
    
    # Mock the side_effect to raise an exception with a string message
    class CustomAPIError(Exception):
        def __init__(self):
            self.args = ("{'sql': 'CREATE TABLE public.test_table (id serial, name text NOT NULL, PRIMARY KEY (id))', 'message': 'Table created successfully', 'success': True, 'table_name': 'public.test_table'}",)
    
    # Set up the mock to raise our custom exception
    mock_rpc = MagicMock()
    mock_supabase.rpc.return_value = mock_rpc
    mock_rpc.execute.side_effect = CustomAPIError()
    
    # Patch the APIError check in the create_table function
    with patch('supabase_mcp_server.postgrest.exceptions.APIError', CustomAPIError):
        # Call the function
        result = supabase_mcp_server.create_table(table_name, columns)
    
    # Verify the result is treated as a success
    assert result["success"] is True
    assert result["message"] == "Table created successfully"
    assert "table_name" in result


def test_execute_sql(mock_supabase):
    """Test executing SQL with the execute_sql tool."""
    # Define test parameters
    sql = "CREATE INDEX idx_test ON test_table (name)"
    
    # Mock the response
    mock_rpc = MagicMock()
    mock_execute = mock_supabase.rpc.return_value.execute.return_value
    mock_supabase.rpc.return_value = mock_rpc
    mock_rpc.execute.return_value = mock_execute
    mock_execute.data = [{"success": True, "message": "SQL executed successfully", "sql": sql}]
    
    # Call the function
    result = supabase_mcp_server.execute_sql(sql)
    
    # Verify the RPC call was made with the correct parameters
    mock_supabase.rpc.assert_called_once_with(
        "execute_sql",
        {"sql": sql}
    )
    
    # Verify the result
    assert result["success"] is True
    assert result["message"] == "SQL executed successfully"
    assert result["sql"] == sql


def test_execute_sql_with_api_error_success(mock_supabase):
    """Test handling APIError that actually contains a success response for execute_sql."""
    # Define test parameters
    sql = "DROP TABLE IF EXISTS test_table"
    
    # Mock an APIError with a success response
    success_response = {
        "sql": sql,
        "message": "SQL executed successfully",
        "success": True
    }
    mock_rpc = MagicMock()
    mock_supabase.rpc.return_value = mock_rpc
    mock_rpc.execute.side_effect = APIError(success_response)
    
    # Call the function
    result = supabase_mcp_server.execute_sql(sql)
    
    # Verify the result is treated as a success
    assert result["success"] is True
    assert result["message"] == "SQL executed successfully"
    assert result["sql"] == sql
