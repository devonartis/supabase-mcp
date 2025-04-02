#!/usr/bin/env python
"""
Test the create_table functionality.

This script tests if tables are actually being created despite the error messages.
"""

import os
import sys
import uuid
import json
import logging
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MCP server
from supabase_mcp_server import create_table, create_records, execute_sql

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_create_table")

def extract_success_data(result):
    """
    Extract success data from the result, handling various formats.
    
    The Supabase client may return success data in different formats:
    1. As a dictionary with success=True
    2. As a string representation of a dictionary
    3. As a nested structure
    
    This function tries to extract the actual success data.
    """
    # If it's already a success dictionary, return it
    if isinstance(result, dict) and result.get('success') is True:
        return result
    
    # If it's a dictionary with a message that contains a success response
    if isinstance(result, dict) and isinstance(result.get('message'), str):
        try:
            # Try to parse the message as JSON
            message = result['message'].replace("'", '"')
            parsed = json.loads(message)
            if isinstance(parsed, dict) and parsed.get('success') is True:
                return parsed
        except Exception:
            pass
    
    # Return the original result
    return result

def test_create_table():
    """Test the create_table function."""
    # Generate a unique table name for testing
    table_name = f"test_table_{uuid.uuid4().hex[:8]}"
    logger.info(f"Testing table creation with table name: {table_name}")
    
    # Define columns for the test table
    columns = [
        {"name": "id", "type": "serial", "primary_key": True},
        {"name": "name", "type": "text", "nullable": False},
        {"name": "value", "type": "integer", "default": "0"}
    ]
    
    # Create the table
    result = create_table(table_name, columns)
    logger.info(f"Table creation result: {result}")
    
    # Extract the actual success data
    success_data = extract_success_data(result)
    
    # Check if the table was created successfully
    success = False
    if isinstance(success_data, dict) and success_data.get('success') is True:
        print(f"✅ Table creation succeeded: {success_data}")
        success = True
    else:
        print(f"❌ Table creation failed: {result}")
        return
    
    # If the table was created successfully, try to insert data
    if success:
        # Wait a moment for the table to be available
        print("Waiting for table to be available...")
        time.sleep(1)  # Wait 1 second
        
        # Try to insert data with retries
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Insert a test record
                test_data = [{"name": "Test Record", "value": 42}]
                insert_result = create_records(table_name, test_data)
                logger.info(f"Successfully inserted data into {table_name}: {insert_result}")
                print(f"✅ Table exists! Successfully inserted data: {insert_result}")
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed to insert data: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"⚠️ Retrying data insertion in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to insert data into {table_name} after {max_retries} attempts: {str(e)}")
                    print(f"❌ Failed to insert data after {max_retries} attempts: {str(e)}")
    
    # Clean up - drop the test table
    try:
        cleanup_result = execute_sql(f"DROP TABLE IF EXISTS {table_name}")
        cleanup_success = extract_success_data(cleanup_result)
        
        if isinstance(cleanup_success, dict) and cleanup_success.get('success') is True:
            logger.info("Successfully cleaned up test table " + table_name)
            print("✅ Successfully cleaned up test table")
        else:
            logger.error(f"Failed to clean up test table {table_name}: {cleanup_result}")
            print(f"⚠️ Failed to clean up test table: {cleanup_result}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        print(f"⚠️ Error during cleanup: {str(e)}")

if __name__ == "__main__":
    test_create_table()
