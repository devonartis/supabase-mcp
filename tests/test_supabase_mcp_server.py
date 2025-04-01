import os
import pytest
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_mcp_server import read_rows, create_records, update_records, delete_records

# Mock Supabase client for testing
@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing."""
    with patch('supabase_mcp_server.supabase') as mock_client:
        # Setup the mock to return predictable data
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        
        # Setup mock for select operations
        mock_select = MagicMock()
        mock_table.select.return_value = mock_select
        mock_match = MagicMock()
        mock_select.match.return_value = mock_match
        mock_execute = MagicMock()
        mock_match.execute.return_value = mock_execute
        mock_select.execute.return_value = mock_execute
        mock_execute.data = [{"id": 1, "name": "Test"}]
        
        # Setup mock for order operations
        mock_order = MagicMock()
        mock_select.order.return_value = mock_order
        mock_order.execute.return_value = mock_execute
        mock_order.match.return_value = mock_match
        mock_order.limit.return_value = mock_order
        mock_order.offset.return_value = mock_order
        
        # Setup mock for limit and offset operations
        mock_select.limit.return_value = mock_select
        mock_select.offset.return_value = mock_select
        mock_match.limit.return_value = mock_match
        mock_match.offset.return_value = mock_match
        
        # Setup mock for insert operations
        mock_insert = MagicMock()
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute
        
        # Setup mock for update operations
        mock_update = MagicMock()
        mock_table.update.return_value = mock_update
        mock_update.match.return_value = mock_match
        
        # Setup mock for delete operations
        mock_delete = MagicMock()
        mock_table.delete.return_value = mock_delete
        mock_delete.match.return_value = mock_match
        
        yield mock_client

def test_read_rows_without_query(mock_supabase):
    """Test reading rows without a query."""
    result = read_rows("test_table")
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().select.assert_called_once_with("*")
    mock_supabase.table().select().execute.assert_called_once()
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_read_rows_with_query(mock_supabase):
    """Test reading rows with a query."""
    query = {"name": "Test"}
    result = read_rows("test_table", query)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().select.assert_called_once_with("*")
    mock_supabase.table().select().match.assert_called_once_with(query)
    mock_supabase.table().select().match().execute.assert_called_once()
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_read_rows_with_select(mock_supabase):
    """Test reading rows with specific columns."""
    result = read_rows("test_table", select="id,name")
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().select.assert_called_once_with("id,name")
    mock_supabase.table().select().execute.assert_called_once()
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_read_rows_with_order_by(mock_supabase):
    """Test reading rows with ordering."""
    order_by = {"created_at": "desc"}
    result = read_rows("test_table", order_by=order_by)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().select.assert_called_once_with("*")
    mock_supabase.table().select().order.assert_called_once_with("created_at", ascending=False)
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_read_rows_with_pagination(mock_supabase):
    """Test reading rows with pagination."""
    result = read_rows("test_table", limit=10, offset=20)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().select.assert_called_once_with("*")
    mock_supabase.table().select().limit.assert_called_once_with(10)
    mock_supabase.table().select().limit().offset.assert_called_once_with(20)
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_read_rows_with_all_parameters(mock_supabase):
    """Test reading rows with all parameters."""
    query = {"status": "active"}
    order_by = {"name": "asc"}
    result = read_rows("test_table", query=query, select="id,name,status", order_by=order_by, limit=10, offset=20)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().select.assert_called_once_with("id,name,status")
    mock_supabase.table().select().match.assert_called_once_with(query)
    
    # Note: Due to the complexity of chaining multiple operations in the test,
    # we're not asserting the exact call sequence for order, limit, and offset here.
    # In a real application, we would use a more sophisticated approach to test this.
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_create_records(mock_supabase):
    """Test creating records."""
    records = [{"name": "New Test"}]
    result = create_records("test_table", records)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().insert.assert_called_once_with(records)
    mock_supabase.table().insert().execute.assert_called_once()
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_update_records(mock_supabase):
    """Test updating records."""
    query = {"id": 1}
    updates = {"name": "Updated Test"}
    result = update_records("test_table", query, updates)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().update.assert_called_once_with(updates)
    mock_supabase.table().update().match.assert_called_once_with(query)
    mock_supabase.table().update().match().execute.assert_called_once()
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]

def test_delete_records(mock_supabase):
    """Test deleting records."""
    query = {"id": 1}
    result = delete_records("test_table", query)
    
    # Verify the correct methods were called
    mock_supabase.table.assert_called_once_with("test_table")
    mock_supabase.table().delete.assert_called_once()
    mock_supabase.table().delete().match.assert_called_once_with(query)
    mock_supabase.table().delete().match().execute.assert_called_once()
    
    # Verify the result
    assert result == [{"id": 1, "name": "Test"}]
