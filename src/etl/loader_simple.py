"""
Data Loader Module - Functional Approach
Loads extracted data into SQLite database using simple functions
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_database(db_path: str) -> sqlite3.Connection:
    """
    Establish database connection
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Database connection object
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"Connected to database: {db_path}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def create_schema(conn: sqlite3.Connection, schema_file: str):
    """
    Create database schema from SQL file
    
    Args:
        conn: Database connection
        schema_file: Path to schema SQL file
    """
    schema_file = Path(schema_file)
    
    if not schema_file.exists():
        logger.error(f"Schema file not found: {schema_file}")
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema created successfully")
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        raise


def load_aggregated_transaction(conn: sqlite3.Connection, records: List[Dict], batch_size: int = 1000):
    """
    Load aggregated transaction data into database
    
    Args:
        conn: Database connection
        records: List of transaction records
        batch_size: Number of records per batch insert
    """
    if not records:
        logger.warning("No transaction records to load")
        return
    
    cursor = conn.cursor()
    
    insert_sql = """
    INSERT OR REPLACE INTO aggregated_transaction 
    (state, year, quarter, transaction_type, transaction_count, transaction_amount)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    try:
        logger.info(f"Loading {len(records)} transaction records...")
        
        for i in tqdm(range(0, len(records), batch_size), desc="Loading transactions"):
            batch = records[i:i + batch_size]
            batch_data = [
                (r['state'], r['year'], r['quarter'], r['transaction_type'], 
                 r['transaction_count'], r['transaction_amount'])
                for r in batch
            ]
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
        
        logger.info("Transaction data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading transaction data: {e}")
        conn.rollback()
        raise


def load_aggregated_user(conn: sqlite3.Connection, records: List[Dict], batch_size: int = 1000):
    """
    Load aggregated user data into database
    
    Args:
        conn: Database connection
        records: List of user records
        batch_size: Number of records per batch insert
    """
    if not records:
        logger.warning("No user records to load")
        return
    
    cursor = conn.cursor()
    
    insert_sql = """
    INSERT OR REPLACE INTO aggregated_user 
    (state, year, quarter, brand, registered_users, app_opens, percentage)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    try:
        logger.info(f"Loading {len(records)} user records...")
        
        for i in tqdm(range(0, len(records), batch_size), desc="Loading users"):
            batch = records[i:i + batch_size]
            batch_data = [
                (r['state'], r['year'], r['quarter'], r['brand'], 
                 r['registered_users'], r['app_opens'], r['percentage'])
                for r in batch
            ]
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
        
        logger.info("User data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        conn.rollback()
        raise


def load_aggregated_insurance(conn: sqlite3.Connection, records: List[Dict], batch_size: int = 1000):
    """
    Load aggregated insurance data into database
    
    Args:
        conn: Database connection
        records: List of insurance records
        batch_size: Number of records per batch insert
    """
    if not records:
        logger.warning("No insurance records to load")
        return
    
    cursor = conn.cursor()
    
    insert_sql = """
    INSERT OR REPLACE INTO aggregated_insurance 
    (state, year, quarter, insurance_type, policy_count, premium_amount)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    try:
        logger.info(f"Loading {len(records)} insurance records...")
        
        for i in tqdm(range(0, len(records), batch_size), desc="Loading insurance"):
            batch = records[i:i + batch_size]
            batch_data = [
                (r['state'], r['year'], r['quarter'], r['insurance_type'], 
                 r['policy_count'], r['premium_amount'])
                for r in batch
            ]
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
        
        logger.info("Insurance data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading insurance data: {e}")
        conn.rollback()
        raise


def load_map_transaction(conn: sqlite3.Connection, records: List[Dict], batch_size: int = 1000):
    """
    Load map transaction data (district-level) into database
    
    Args:
        conn: Database connection
        records: List of district transaction records
        batch_size: Number of records per batch insert
    """
    if not records:
        logger.warning("No map transaction records to load")
        return
    
    cursor = conn.cursor()
    
    insert_sql = """
    INSERT OR REPLACE INTO map_transaction 
    (state, year, quarter, district, transaction_count, transaction_amount)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    try:
        logger.info(f"Loading {len(records)} district-level transaction records...")
        
        for i in tqdm(range(0, len(records), batch_size), desc="Loading map transactions"):
            batch = records[i:i + batch_size]
            batch_data = [
                (r['state'], r['year'], r['quarter'], r['district'], 
                 r['transaction_count'], r['transaction_amount'])
                for r in batch
            ]
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
        
        logger.info("Map transaction data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading map transaction data: {e}")
        conn.rollback()
        raise


def get_table_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    """
    Get record counts for all tables
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary of table names and their record counts
    """
    cursor = conn.cursor()
    tables = ['aggregated_transaction', 'aggregated_user', 'aggregated_insurance', 'map_transaction']
    counts = {}
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except:
            counts[table] = 0
    
    return counts
