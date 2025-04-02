#!/usr/bin/env python
"""
Deploy SQL functions to Supabase.

This script reads SQL function definitions from files and deploys them to a Supabase database.
It requires the SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables to be set.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import logger
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logger

# Configure logging
logger = logger.get_logger("deploy_sql")

def deploy_sql_function(supabase: Client, sql_file_path: str) -> bool:
    """
    Deploy a SQL function to Supabase.
    
    Args:
        supabase: Supabase client
        sql_file_path: Path to the SQL file containing the function definition
        
    Returns:
        bool: True if deployment was successful, False otherwise
    """
    try:
        # Read the SQL file
        with open(sql_file_path, 'r') as file:
            sql = file.read()
        
        # Log the deployment
        logger.info(f"Deploying SQL function from {sql_file_path}")
        
        # Execute the SQL
        result = supabase.rpc('pgexecute', {'query': sql}).execute()
        
        # Check for errors
        if hasattr(result, 'error') and result.error:
            logger.error(f"Error deploying SQL function: {result.error}")
            return False
        
        logger.info(f"Successfully deployed SQL function from {sql_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deploying SQL function: {str(e)}", exc_info=e)
        return False

def main():
    """Main function to deploy SQL functions."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Deploy SQL functions to Supabase')
    parser.add_argument('--sql-dir', default='sql', help='Directory containing SQL files')
    parser.add_argument('--file', help='Specific SQL file to deploy (relative to sql-dir)')
    args = parser.parse_args()
    
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
    
    # Determine which SQL files to deploy
    sql_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), args.sql_dir)
    
    if args.file:
        # Deploy a specific file
        sql_file_path = os.path.join(sql_dir, args.file)
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL file not found: {sql_file_path}")
            sys.exit(1)
        
        success = deploy_sql_function(supabase, sql_file_path)
        sys.exit(0 if success else 1)
    else:
        # Deploy all SQL files in the directory
        if not os.path.exists(sql_dir):
            logger.error(f"SQL directory not found: {sql_dir}")
            sys.exit(1)
        
        # Get all .sql files
        sql_files = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
        if not sql_files:
            logger.warning(f"No SQL files found in {sql_dir}")
            sys.exit(0)
        
        # Deploy each file
        success = True
        for sql_file in sql_files:
            sql_file_path = os.path.join(sql_dir, sql_file)
            file_success = deploy_sql_function(supabase, sql_file_path)
            success = success and file_success
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
