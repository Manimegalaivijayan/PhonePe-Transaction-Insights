-- ============================================
-- BUSINESS CASE 1: Decoding Transaction Dynamics
-- ============================================
-- Understanding transaction behavior variations across states, quarters, and payment categories

-- 1.1 Overall Transaction Trends (Year-over-Year Growth)
-- Shows total transactions and growth rate by year
SELECT 
    year,
    SUM(transaction_count) as total_transactions,
    SUM(transaction_amount) as total_amount,
    ROUND(SUM(transaction_amount) / 1e9, 2) as amount_in_billions,
    LAG(SUM(transaction_count)) OVER (ORDER BY year) as prev_year_count,
    ROUND(
        (SUM(transaction_count) - LAG(SUM(transaction_count)) OVER (ORDER BY year)) * 100.0 
        / NULLIF(LAG(SUM(transaction_count)) OVER (ORDER BY year), 0), 2
    ) as yoy_growth_pct
FROM aggregated_transaction
WHERE state = 'All India'
GROUP BY year
ORDER BY year;

-- 1.2 Transaction Type Performance
-- Identifies which transaction types are growing or declining
SELECT 
    transaction_type,
    SUM(transaction_count) as total_transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount_billions,
    ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_transaction_value,
    COUNT(DISTINCT year || '-' || quarter) as quarters_present
FROM aggregated_transaction
WHERE state = 'All India'
GROUP BY transaction_type
ORDER BY total_amount_billions DESC;

-- 1.3 Seasonal Pattern Analysis (Quarter-wise)
-- Shows if certain quarters have higher transaction activity
SELECT 
    quarter,
    ROUND(AVG(transaction_count), 0) as avg_transactions,
    ROUND(AVG(transaction_amount) / 1e9, 2) as avg_amount_billions,
    COUNT(*) as sample_size
FROM aggregated_transaction
WHERE state = 'All India' AND year >= 2020
GROUP BY quarter
ORDER BY quarter;

-- 1.4 Transaction Type Growth by Year
-- Detailed view of each payment category's performance over time
SELECT 
    year,
    transaction_type,
    SUM(transaction_count) as transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
FROM aggregated_transaction
WHERE state = 'All India'
GROUP BY year, transaction_type
ORDER BY year, amount_billions DESC;

-- 1.5 States with Declining Transactions
-- Identifies states that need attention
WITH state_trends AS (
    SELECT 
        state,
        year,
        SUM(transaction_count) as yearly_transactions
    FROM aggregated_transaction
    WHERE state != 'All India'
    GROUP BY state, year
),
growth_calc AS (
    SELECT 
        state,
        year,
        yearly_transactions,
        LAG(yearly_transactions) OVER (PARTITION BY state ORDER BY year) as prev_year,
        yearly_transactions - LAG(yearly_transactions) OVER (PARTITION BY state ORDER BY year) as growth
    FROM state_trends
)
SELECT 
    state,
    MAX(CASE WHEN year = 2023 THEN yearly_transactions END) as transactions_2023,
    MAX(CASE WHEN year = 2022 THEN yearly_transactions END) as transactions_2022,
    ROUND(
        (MAX(CASE WHEN year = 2023 THEN yearly_transactions END) - 
         MAX(CASE WHEN year = 2022 THEN yearly_transactions END)) * 100.0 /
        NULLIF(MAX(CASE WHEN year = 2022 THEN yearly_transactions END), 0), 2
    ) as growth_pct
FROM growth_calc
WHERE year IN (2022, 2023)
GROUP BY state
HAVING growth_pct < 0
ORDER BY growth_pct;

-- 1.6 Transaction Count vs Amount Correlation
-- Shows if high transaction count correlates with high value
SELECT 
    transaction_type,
    year,
    quarter,
    transaction_count,
    ROUND(transaction_amount / 1e6, 2) as amount_millions,
    ROUND(transaction_amount / NULLIF(transaction_count, 0), 2) as avg_ticket_size
FROM aggregated_transaction
WHERE state = 'All India' AND year >= 2022
ORDER BY year DESC, quarter DESC, transaction_count DESC;

-- 1.7 Top Growing Transaction Types (Latest Year)
-- Identifies trending payment categories
WITH recent_data AS (
    SELECT 
        transaction_type,
        year,
        SUM(transaction_count) as yearly_transactions
    FROM aggregated_transaction
    WHERE state = 'All India' AND year >= 2022
    GROUP BY transaction_type, year
)
SELECT 
    transaction_type,
    MAX(CASE WHEN year = 2023 THEN yearly_transactions END) as trans_2023,
    MAX(CASE WHEN year = 2022 THEN yearly_transactions END) as trans_2022,
    ROUND(
        (MAX(CASE WHEN year = 2023 THEN yearly_transactions END) - 
         MAX(CASE WHEN year = 2022 THEN yearly_transactions END)) * 100.0 /
        NULLIF(MAX(CASE WHEN year = 2022 THEN yearly_transactions END), 0), 2
    ) as growth_rate_pct
FROM recent_data
GROUP BY transaction_type
ORDER BY growth_rate_pct DESC;
