"""
Integration test for the Supabase MCP server.

This script tests the Supabase MCP server with a real Supabase instance.
To run this test, you need to have a Supabase project and set the
SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.

Example:
    $ python -m tests.integration_test
"""

import os
import sys
import json
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the server module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_mcp_server import read_rows, create_records, update_records, delete_records

# Test configuration
TEST_TABLE = "test_table"  # Make sure this table exists in your Supabase project

def test_crud_operations():
    """Test the CRUD operations with a real Supabase instance."""
    print("\n=== Starting Integration Test ===")
    
    # Check if environment variables are set
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_SERVICE_ROLE_KEY'):
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.")
        return False
    
    try:
        # 1. Create a test record
        test_record = {
            "name": "Integration Test",
            "description": "Testing the Supabase MCP server",
            "created_at": "2025-03-31T00:00:00"
        }
        
        print(f"\n1. Creating record in {TEST_TABLE}...")
        created = create_records(TEST_TABLE, [test_record])
        if not created or not isinstance(created, list) or len(created) == 0:
            print(f"Error: Failed to create record. Result: {created}")
            return False
        
        print(f"✓ Record created: {json.dumps(created[0], indent=2)}")
        record_id = created[0].get('id')
        
        # 2. Read the created record
        print(f"\n2. Reading record with id={record_id}...")
        read = read_rows(TEST_TABLE, {"id": record_id})
        if not read or not isinstance(read, list) or len(read) == 0:
            print(f"Error: Failed to read record. Result: {read}")
            return False
        
        print(f"✓ Record read: {json.dumps(read[0], indent=2)}")
        
        # 3. Update the record
        update_data = {"description": "Updated description"}
        print(f"\n3. Updating record with id={record_id}...")
        updated = update_records(TEST_TABLE, {"id": record_id}, update_data)
        if not updated or not isinstance(updated, list) or len(updated) == 0:
            print(f"Error: Failed to update record. Result: {updated}")
            return False
        
        print(f"✓ Record updated: {json.dumps(updated[0], indent=2)}")
        
        # 4. Read the updated record to verify
        print(f"\n4. Reading updated record with id={record_id}...")
        read_updated = read_rows(TEST_TABLE, {"id": record_id})
        if not read_updated or not isinstance(read_updated, list) or len(read_updated) == 0:
            print(f"Error: Failed to read updated record. Result: {read_updated}")
            return False
        
        if read_updated[0].get('description') != update_data['description']:
            print(f"Error: Update verification failed. Expected '{update_data['description']}' but got '{read_updated[0].get('description')}'")
            return False
        
        print(f"✓ Updated record verified: {json.dumps(read_updated[0], indent=2)}")
        
        # 5. Delete the record
        print(f"\n5. Deleting record with id={record_id}...")
        deleted = delete_records(TEST_TABLE, {"id": record_id})
        if not deleted or not isinstance(deleted, list) or len(deleted) == 0:
            print(f"Error: Failed to delete record. Result: {deleted}")
            return False
        
        print(f"✓ Record deleted: {json.dumps(deleted[0], indent=2)}")
        
        # 6. Verify deletion
        print(f"\n6. Verifying deletion of record with id={record_id}...")
        read_after_delete = read_rows(TEST_TABLE, {"id": record_id})
        if read_after_delete and isinstance(read_after_delete, list) and len(read_after_delete) > 0:
            print(f"Error: Record still exists after deletion. Result: {read_after_delete}")
            return False
        
        print("✓ Deletion verified: Record no longer exists")
        
        print("\n=== Integration Test Successful! ===")
        return True
        
    except Exception as e:
        print(f"Error during integration test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_crud_operations()
    sys.exit(0 if success else 1)
