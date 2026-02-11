-- PhonePe Pulse SQLite Database Schema
-- Created: February 2026
-- Database: phonepe_pulse.db

-- ============================================
-- AGGREGATED TABLES
-- ============================================

-- Aggregated Transaction Data
-- Source: data/aggregated/transaction/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS aggregated_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    transaction_type VARCHAR(100) NOT NULL,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    transaction_amount REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, year, quarter, transaction_type)
);

-- Aggregated User Data
-- Source: data/aggregated/user/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS aggregated_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    brand VARCHAR(50),
    registered_users INTEGER NOT NULL DEFAULT 0,
    app_opens INTEGER NOT NULL DEFAULT 0,
    percentage REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, year, quarter, brand)
);

-- Aggregated Insurance Data
-- Source: data/aggregated/insurance/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS aggregated_insurance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    insurance_type VARCHAR(50),
    insurance_count INTEGER NOT NULL DEFAULT 0,
    insurance_amount REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, year, quarter, insurance_type)
);

-- ============================================
-- MAP TABLES (District Level)
-- ============================================

-- Map Transaction Data
-- Source: data/map/transaction/hover/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS map_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    transaction_count INTEGER NOT NULL DEFAULT 0,
    transaction_amount REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, district, year, quarter)
);

-- Map User Data
-- Source: data/map/user/hover/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS map_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    registered_users INTEGER NOT NULL DEFAULT 0,
    app_opens INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, district, year, quarter)
);

-- Map Insurance Data
-- Source: data/map/insurance/hover/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS map_insurance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    insurance_count INTEGER NOT NULL DEFAULT 0,
    insurance_amount REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, district, year, quarter)
);

-- ============================================
-- TOP TABLES (Best Performers)
-- ============================================

-- Top Transaction Data (States, Districts & Pincodes)
-- Source: data/top/transaction/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS top_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100),
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('state', 'district', 'pincode')),
    entity_name VARCHAR(100) NOT NULL,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    transaction_amount REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, year, quarter, entity_type, entity_name)
);

-- Top User Data (States, Districts & Pincodes)
-- Source: data/top/user/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS top_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100),
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('state', 'district', 'pincode')),
    entity_name VARCHAR(100) NOT NULL,
    registered_users INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, year, quarter, entity_type, entity_name)
);

-- Top Insurance Data (States, Districts & Pincodes)
-- Source: data/top/insurance/country/india/{year}/{quarter}.json
CREATE TABLE IF NOT EXISTS top_insurance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state VARCHAR(100),
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('state', 'district', 'pincode')),
    entity_name VARCHAR(100) NOT NULL,
    insurance_count INTEGER NOT NULL DEFAULT 0,
    insurance_amount REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state, year, quarter, entity_type, entity_name)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Aggregated Transaction Indexes
CREATE INDEX IF NOT EXISTS idx_agg_trans_state_year ON aggregated_transaction(state, year);
CREATE INDEX IF NOT EXISTS idx_agg_trans_type ON aggregated_transaction(transaction_type);
CREATE INDEX IF NOT EXISTS idx_agg_trans_quarter ON aggregated_transaction(quarter);

-- Aggregated User Indexes
CREATE INDEX IF NOT EXISTS idx_agg_user_state_year ON aggregated_user(state, year);
CREATE INDEX IF NOT EXISTS idx_agg_user_brand ON aggregated_user(brand);

-- Aggregated Insurance Indexes
CREATE INDEX IF NOT EXISTS idx_agg_ins_state_year ON aggregated_insurance(state, year);

-- Map Transaction Indexes
CREATE INDEX IF NOT EXISTS idx_map_trans_state ON map_transaction(state);
CREATE INDEX IF NOT EXISTS idx_map_trans_district ON map_transaction(district);

-- Map User Indexes
CREATE INDEX IF NOT EXISTS idx_map_user_state ON map_user(state);
CREATE INDEX IF NOT EXISTS idx_map_user_district ON map_user(district);

-- Top Transaction Indexes
CREATE INDEX IF NOT EXISTS idx_top_trans_state ON top_transaction(state);
CREATE INDEX IF NOT EXISTS idx_top_trans_type ON top_transaction(entity_type);
CREATE INDEX IF NOT EXISTS idx_top_trans_year_quarter ON top_transaction(year, quarter);

-- Top User Indexes
CREATE INDEX IF NOT EXISTS idx_top_user_state ON top_user(state);
CREATE INDEX IF NOT EXISTS idx_top_user_type ON top_user(entity_type);
