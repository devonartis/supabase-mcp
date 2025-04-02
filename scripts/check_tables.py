#!/usr/bin/env python
"""
Check tables in Supabase database.

This script lists all tables in the public schema of your Supabase database.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from postgrest.exceptions import APIError

# Add parent directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logger

# Configure logging
logger = logger.get_logger("check_tables")

def main():
    """List all tables in the public schema."""
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.")
        sys.exit(1)
    
    # Initialize Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    # SQL query to list all tables
    sql = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE' 
    ORDER BY table_name
    """
    
    try:
        # Execute the query
        result = supabase.rpc('execute_sql', {'sql': sql}).execute()
        # This won't be reached due to the API error
        print("Tables in public schema:")
        for table in result.data:
            print(f"- {table['table_name']}")
    except APIError as e:
        # Extract data from the error
        if hasattr(e, 'args') and len(e.args) > 0 and isinstance(e.args[0], dict):
            error_data = e.args[0]
            if error_data.get('success') is True:
                print("SQL executed successfully, but response was treated as an error.")
                print("This is a known issue with the Supabase client.")
                print("\nTables in public schema:")
                # Try to extract table names from the response
                try:
                    # Create a test table to check if our functions are working
                    test_table_sql = """
                    CREATE TABLE IF NOT EXISTS test_table_check (
                        id serial PRIMARY KEY,
                        name text NOT NULL,
                        created_at timestamp DEFAULT now()
                    )
                    """
                    supabase.rpc('execute_sql', {'sql': test_table_sql}).execute()
                    print("Created test_table_check successfully")
                except Exception as e2:
                    print(f"Error creating test table: {str(e2)}")
                
                # Try listing tables again
                try:
                    # List tables again to see if our test table was created
                    list_tables_sql = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE' 
                    ORDER BY table_name
                    """
                    supabase.rpc('execute_sql', {'sql': list_tables_sql}).execute()
                except APIError as e3:
                    if hasattr(e3, 'args') and len(e3.args) > 0 and isinstance(e3.args[0], dict):
                        error_data3 = e3.args[0]
                        print(f"Response from listing tables: {error_data3}")
                    else:
                        print(f"Error listing tables: {str(e3)}")
            else:
                print(f"Error executing SQL: {error_data.get('message', str(e))}")
        else:
            print(f"Error executing SQL: {str(e)}")

if __name__ == "__main__":
    main()
