"""
SQL Query Executor - Functional Approach
Executes business case queries using simple functions
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_database(db_path: str) -> sqlite3.Connection:
    """
    Establish database connection
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Database connection object
    """
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    logger.info(f"Connected to database: {db_path}")
    return conn


def execute_query(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    """
    Execute a single SQL query
    
    Args:
        conn: Database connection
        query: SQL query string
        
    Returns:
        pandas DataFrame with query results
    """
    try:
        df = pd.read_sql_query(query, conn)
        logger.info(f"Query executed successfully. Rows returned: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


def execute_query_file(conn: sqlite3.Connection, file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Execute all queries from a SQL file
    
    Args:
        conn: Database connection
        file_path: Path to SQL file with queries
        
    Returns:
        Dictionary of query results {query_name: DataFrame}
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"Query file not found: {file_path}")
        raise FileNotFoundError(f"Query file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        sql_content = f.read()
    
    # Split queries by comments that start with "-- Query:"
    queries = {}
    current_query_name = None
    current_query = []
    
    for line in sql_content.split('\n'):
        if line.strip().startswith('-- Query:'):
            if current_query_name and current_query:
                query_text = '\n'.join(current_query).strip()
                if query_text:
                    queries[current_query_name] = query_text
            current_query_name = line.replace('-- Query:', '').strip()
            current_query = []
        elif not line.strip().startswith('--'):
            current_query.append(line)
    
    # Add last query
    if current_query_name and current_query:
        query_text = '\n'.join(current_query).strip()
        if query_text:
            queries[current_query_name] = query_text
    
    # Execute all queries
    results = {}
    for name, query in queries.items():
        try:
            results[name] = execute_query(conn, query)
            logger.info(f"Executed query: {name}")
        except Exception as e:
            logger.error(f"Error in query {name}: {e}")
    
    return results


def get_case_1_data(conn: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """Execute Case 1: Transaction Dynamics queries"""
    base_dir = Path(__file__).parent.parent.parent
    query_file = base_dir / "sql" / "queries" / "case_1_transaction_dynamics.sql"
    return execute_query_file(conn, str(query_file))


def get_case_2_data(conn: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """Execute Case 2: Device Dominance queries"""
    base_dir = Path(__file__).parent.parent.parent
    query_file = base_dir / "sql" / "queries" / "case_2_device_engagement.sql"
    return execute_query_file(conn, str(query_file))


def get_case_4_data(conn: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """Execute Case 4: Market Expansion queries"""
    base_dir = Path(__file__).parent.parent.parent
    query_file = base_dir / "sql" / "queries" / "case_4_market_expansion.sql"
    return execute_query_file(conn, str(query_file))


def get_case_5_data(conn: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """Execute Case 5: User Engagement queries"""
    base_dir = Path(__file__).parent.parent.parent
    query_file = base_dir / "sql" / "queries" / "case_5_user_engagement.sql"
    return execute_query_file(conn, str(query_file))


def get_case_7_data(conn: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """Execute Case 7: State & District Analysis queries"""
    base_dir = Path(__file__).parent.parent.parent
    query_file = base_dir / "sql" / "queries" / "case_7_state_district_analysis.sql"
    return execute_query_file(conn, str(query_file))


def test_queries():
    """Test function to demonstrate query execution"""
    base_dir = Path(__file__).parent.parent.parent
    db_path = base_dir / "data" / "phonepe_pulse.db"
    
    print("=" * 80)
    print("Testing PhonePe Pulse Query Executor (Functional Approach)")
    print("=" * 80)
    
    # Connect to database
    conn = connect_database(str(db_path))
    
    try:
        # Test Case 1: Transaction Dynamics
        print("\n📊 Case 1: Transaction Dynamics")
        print("-" * 80)
        case1_results = get_case_1_data(conn)
        
        if "1. Transaction Summary by Year" in case1_results:
            df = case1_results["1. Transaction Summary by Year"]
            print("\nTransaction Summary (2018-2024):")
            print(df.to_string(index=False))
        
        if "2. Transaction Type Performance" in case1_results:
            df = case1_results["2. Transaction Type Performance"]
            print("\nTop Transaction Types:")
            print(df.head().to_string(index=False))
        
        # Test Case 2: Device Engagement
        print("\n\n📱 Case 2: Device Dominance & User Engagement")
        print("-" * 80)
        case2_results = get_case_2_data(conn)
        
        if "1. Device Brand Market Share" in case2_results:
            df = case2_results["1. Device Brand Market Share"]
            print("\nTop Device Brands:")
            print(df.head(10).to_string(index=False))
        
        # Test Case 7: State Analysis
        print("\n\n🗺️  Case 7: State & District Analysis")
        print("-" * 80)
        case7_results = get_case_7_data(conn)
        
        if "1. Top 10 States by Transaction Volume" in case7_results:
            df = case7_results["1. Top 10 States by Transaction Volume"]
            print("\nTop 10 States:")
            print(df.to_string(index=False))
        
        print("\n" + "=" * 80)
        print("✅ All tests completed successfully!")
        print("=" * 80)
        
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    test_queries()
