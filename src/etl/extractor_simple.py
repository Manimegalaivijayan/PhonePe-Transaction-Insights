"""
Data Extractor Module - Functional Approach
Extracts JSON data from PhonePe Pulse repository using simple functions
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from git import Repo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clone_or_pull_repo(repo_url: str, local_path: str) -> bool:
    """
    Clone repository if not exists, otherwise pull latest changes
    
    Args:
        repo_url: GitHub repository URL
        local_path: Local path to clone/store data
        
    Returns:
        bool: Success status
    """
    try:
        local_path = Path(local_path)
        if local_path.exists():
            logger.info(f"Repository exists. Pulling latest changes...")
            repo = Repo(local_path)
            origin = repo.remotes.origin
            origin.pull()
            logger.info("Repository updated successfully")
        else:
            logger.info(f"Cloning repository from {repo_url}...")
            Repo.clone_from(repo_url, local_path)
            logger.info("Repository cloned successfully")
        return True
    except Exception as e:
        logger.error(f"Error with repository: {e}")
        return False


def _process_aggregated_transaction(file_path: Path, state: str, year: int, quarter: int) -> List[Dict]:
    """Process aggregated transaction JSON file"""
    records = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if 'data' in data and 'transactionData' in data['data']:
            for item in data['data']['transactionData']:
                records.append({
                    'state': state,
                    'year': year,
                    'quarter': quarter,
                    'transaction_type': item['name'],
                    'transaction_count': item['paymentInstruments'][0]['count'],
                    'transaction_amount': item['paymentInstruments'][0]['amount']
                })
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return records


def _process_aggregated_user(file_path: Path, state: str, year: int, quarter: int) -> List[Dict]:
    """Process aggregated user JSON file"""
    records = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'data' in data and 'usersByDevice' in data['data']:
            for item in data['data']['usersByDevice']:
                records.append({
                    'state': state,
                    'year': year,
                    'quarter': quarter,
                    'brand': item['brand'],
                    'registered_users': item['count'],
                    'app_opens': item.get('appOpens', 0),
                    'percentage': item.get('percentage', 0)
                })
        
        # Also add total aggregated users
        if 'data' in data and 'aggregated' in data['data']:
            agg = data['data']['aggregated']
            records.append({
                'state': state,
                'year': year,
                'quarter': quarter,
                'brand': 'Total',
                'registered_users': agg.get('registeredUsers', 0),
                'app_opens': agg.get('appOpens', 0),
                'percentage': 1.0
            })
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return records


def _process_aggregated_insurance(file_path: Path, state: str, year: int, quarter: int) -> List[Dict]:
    """Process aggregated insurance JSON file"""
    records = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'data' in data and 'transactionData' in data['data']:
            for item in data['data']['transactionData']:
                records.append({
                    'state': state,
                    'year': year,
                    'quarter': quarter,
                    'insurance_type': item['name'],
                    'policy_count': item['paymentInstruments'][0]['count'],
                    'premium_amount': item['paymentInstruments'][0]['amount']
                })
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return records


def extract_aggregated_transaction_data(data_path: str) -> List[Dict]:
    """
    Extract aggregated transaction data from JSON files
    
    Args:
        data_path: Path to pulse repository data folder
        
    Returns:
        List of transaction records
    """
    data_path = Path(data_path)
    aggregated_path = data_path / "data" / "aggregated" / "transaction" / "country" / "india"
    
    if not aggregated_path.exists():
        logger.warning(f"Path not found: {aggregated_path}")
        return []
    
    all_records = []
    logger.info("Extracting aggregated transaction data...")
    
    # Process state-level data
    for state_dir in aggregated_path.iterdir():
        if not state_dir.is_dir():
            continue
            
        state_name = state_dir.name
        
        for year_dir in state_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            try:
                year = int(year_dir.name)
            except ValueError:
                continue
            
            for quarter_file in year_dir.glob("*.json"):
                try:
                    quarter = int(quarter_file.stem)
                    records = _process_aggregated_transaction(quarter_file, state_name, year, quarter)
                    all_records.extend(records)
                except Exception as e:
                    logger.error(f"Error processing {quarter_file}: {e}")
    
    logger.info(f"Extracted {len(all_records)} transaction records")
    return all_records


def extract_aggregated_user_data(data_path: str) -> List[Dict]:
    """
    Extract aggregated user data from JSON files
    
    Args:
        data_path: Path to pulse repository data folder
        
    Returns:
        List of user records
    """
    data_path = Path(data_path)
    aggregated_path = data_path / "data" / "aggregated" / "user" / "country" / "india"
    
    if not aggregated_path.exists():
        logger.warning(f"Path not found: {aggregated_path}")
        return []
    
    all_records = []
    logger.info("Extracting aggregated user data...")
    
    for state_dir in aggregated_path.iterdir():
        if not state_dir.is_dir():
            continue
            
        state_name = state_dir.name
        
        for year_dir in state_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            try:
                year = int(year_dir.name)
            except ValueError:
                continue
            
            for quarter_file in year_dir.glob("*.json"):
                try:
                    quarter = int(quarter_file.stem)
                    records = _process_aggregated_user(quarter_file, state_name, year, quarter)
                    all_records.extend(records)
                except Exception as e:
                    logger.error(f"Error processing {quarter_file}: {e}")
    
    logger.info(f"Extracted {len(all_records)} user records")
    return all_records


def extract_aggregated_insurance_data(data_path: str) -> List[Dict]:
    """
    Extract aggregated insurance data from JSON files
    
    Args:
        data_path: Path to pulse repository data folder
        
    Returns:
        List of insurance records
    """
    data_path = Path(data_path)
    aggregated_path = data_path / "data" / "aggregated" / "insurance" / "country" / "india"
    
    if not aggregated_path.exists():
        logger.warning(f"Path not found: {aggregated_path}")
        return []
    
    all_records = []
    logger.info("Extracting aggregated insurance data...")
    
    for state_dir in aggregated_path.iterdir():
        if not state_dir.is_dir():
            continue
            
        state_name = state_dir.name
        
        for year_dir in state_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            try:
                year = int(year_dir.name)
            except ValueError:
                continue
            
            for quarter_file in year_dir.glob("*.json"):
                try:
                    quarter = int(quarter_file.stem)
                    records = _process_aggregated_insurance(quarter_file, state_name, year, quarter)
                    all_records.extend(records)
                except Exception as e:
                    logger.error(f"Error processing {quarter_file}: {e}")
    
    logger.info(f"Extracted {len(all_records)} insurance records")
    return all_records


def _process_map_transaction(file_path: Path, state: str, year: int, quarter: int) -> List[Dict]:
    """Process map transaction JSON file (district-level)"""
    records = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if 'data' in data and 'hoverDataList' in data['data']:
            for item in data['data']['hoverDataList']:
                district_name = item['name']
                records.append({
                    'state': state,
                    'year': year,
                    'quarter': quarter,
                    'district': district_name,
                    'transaction_count': item['metric'][0]['count'],
                    'transaction_amount': item['metric'][0]['amount']
                })
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return records


def extract_map_transaction_data(data_path: str) -> List[Dict]:
    """
    Extract map transaction data (district-level) from JSON files
    
    Args:
        data_path: Path to pulse repository data folder
        
    Returns:
        List of district-level transaction records
    """
    data_path = Path(data_path)
    map_path = data_path / "data" / "map" / "transaction" / "hover" / "country" / "india" / "state"
    
    if not map_path.exists():
        logger.warning(f"Path not found: {map_path}")
        return []
    
    all_records = []
    logger.info("Extracting map transaction data (district-level)...")
    
    for state_dir in map_path.iterdir():
        if not state_dir.is_dir():
            continue
            
        state_name = state_dir.name
        
        for year_dir in state_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            try:
                year = int(year_dir.name)
            except ValueError:
                continue
            
            # Process quarter JSON files (1.json, 2.json, 3.json, 4.json)
            for quarter_file in year_dir.glob("*.json"):
                try:
                    quarter = int(quarter_file.stem)
                    records = _process_map_transaction(
                        quarter_file, state_name, year, quarter
                    )
                    all_records.extend(records)
                except Exception as e:
                    logger.error(f"Error processing {quarter_file}: {e}")
    
    logger.info(f"Extracted {len(all_records)} district-level transaction records")
    return all_records
