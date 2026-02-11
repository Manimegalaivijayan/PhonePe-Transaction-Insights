"""
Main ETL Pipeline - Functional Approach
Orchestrates data extraction and loading using simple functions
"""

import yaml
import logging
from pathlib import Path

# Import functional modules
import sys
sys.path.append(str(Path(__file__).parent))

from extractor_simple import (
    clone_or_pull_repo,
    extract_aggregated_transaction_data,
    extract_aggregated_user_data,
    extract_aggregated_insurance_data
)

from loader_simple import (
    connect_database,
    create_schema,
    load_aggregated_transaction,
    load_aggregated_user,
    load_aggregated_insurance,
    get_table_counts
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from YAML file"""
    # Get the project root directory (3 levels up from this file)
    base_dir = Path(__file__).parent.parent.parent
    config_path = base_dir / "config" / "config.yaml"
    
    logger.info(f"Loading configuration from: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def main():
    """Main ETL pipeline execution"""
    logger.info("=" * 80)
    logger.info("PhonePe Pulse Data ETL Pipeline - Functional Approach")
    logger.info("=" * 80)
    
    # Load configuration
    config = load_config()
    
    base_dir = Path(__file__).parent.parent.parent
    repo_path = base_dir / config['data_source']['local_path']
    db_path = base_dir / config['database']['path']
    schema_path = base_dir / config['database']['schema_file']
    
    logger.info(f"Repository path: {repo_path}")
    logger.info(f"Database path: {db_path}")
    
    # Step 1: Clone or update repository
    logger.info("\n" + "=" * 80)
    logger.info("Step 1: Cloning/Updating Repository")
    logger.info("=" * 80)
    
    success = clone_or_pull_repo(
        config['data_source']['github_repo'],
        str(repo_path)
    )
    
    if not success:
        logger.error("Failed to clone/update repository")
        return
    
    # Step 2: Extract data
    logger.info("\n" + "=" * 80)
    logger.info("Step 2: Extracting Data")
    logger.info("=" * 80)
    
    transaction_records = extract_aggregated_transaction_data(str(repo_path))
    user_records = extract_aggregated_user_data(str(repo_path))
    insurance_records = extract_aggregated_insurance_data(str(repo_path))
    
    logger.info(f"\nExtraction Summary:")
    logger.info(f"  - Transactions: {len(transaction_records)} records")
    logger.info(f"  - Users: {len(user_records)} records")
    logger.info(f"  - Insurance: {len(insurance_records)} records")
    logger.info(f"  - Total: {len(transaction_records) + len(user_records) + len(insurance_records)} records")
    
    # Step 3: Setup database
    logger.info("\n" + "=" * 80)
    logger.info("Step 3: Setting Up Database")
    logger.info("=" * 80)
    
    conn = connect_database(str(db_path))
    
    try:
        create_schema(conn, str(schema_path))
        
        # Step 4: Load data
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: Loading Data into Database")
        logger.info("=" * 80)
        
        load_aggregated_transaction(conn, transaction_records)
        load_aggregated_user(conn, user_records)
        load_aggregated_insurance(conn, insurance_records)
        
        # Step 5: Verify data
        logger.info("\n" + "=" * 80)
        logger.info("Step 5: Verifying Data")
        logger.info("=" * 80)
        
        counts = get_table_counts(conn)
        
        logger.info("\nFinal Database Record Counts:")
        for table, count in counts.items():
            logger.info(f"  - {table}: {count} records")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ETL Pipeline Completed Successfully!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error in ETL pipeline: {e}")
        raise
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    main()
