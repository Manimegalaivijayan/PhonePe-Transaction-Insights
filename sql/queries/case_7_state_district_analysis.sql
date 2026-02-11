-- ============================================
-- BUSINESS CASE 7: Transaction Analysis Across States and Districts
-- ============================================
-- Identifying top performers for targeted marketing

-- 7.1 Top 10 States by Transaction Volume
-- Highest transaction states overall
SELECT 
    state,
    SUM(transaction_count) as total_transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount_billions,
    COUNT(DISTINCT transaction_type) as payment_types,
    ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_transaction_value
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2022
GROUP BY state
ORDER BY total_transactions DESC
LIMIT 10;

-- 7.2 Top 10 States by Transaction Amount
-- Highest value states
SELECT 
    state,
    ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount_billions,
    SUM(transaction_count) as total_transactions,
    ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_ticket_size,
    COUNT(DISTINCT year || '-' || quarter) as quarters_active
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2022
GROUP BY state
ORDER BY total_amount_billions DESC
LIMIT 10;

-- 7.3 Transaction Concentration Analysis
-- How concentrated are transactions in top states?
WITH state_totals AS (
    SELECT 
        state,
        SUM(transaction_count) as state_transactions,
        (SELECT SUM(transaction_count) FROM aggregated_transaction 
         WHERE state != 'All India' AND year >= 2022) as grand_total
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2022
    GROUP BY state
)
SELECT 
    state,
    state_transactions,
    ROUND(state_transactions * 100.0 / grand_total, 2) as market_share_pct,
    SUM(ROUND(state_transactions * 100.0 / grand_total, 2)) 
        OVER (ORDER BY state_transactions DESC) as cumulative_share_pct,
    ROW_NUMBER() OVER (ORDER BY state_transactions DESC) as rank
FROM state_totals
ORDER BY state_transactions DESC
LIMIT 15;

-- 7.4 High-Value Transaction States
-- States with highest average transaction values
SELECT 
    state,
    SUM(transaction_count) as total_transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount_billions,
    ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_transaction_value,
    MAX(transaction_amount / NULLIF(transaction_count, 0)) as max_avg_value
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2022
GROUP BY state
HAVING SUM(transaction_count) > 1000000  -- At least 1M transactions
ORDER BY avg_transaction_value DESC
LIMIT 15;

-- 7.5 Quarterly Performance Leaders
-- Top states in recent quarters
SELECT 
    year,
    quarter,
    state,
    SUM(transaction_count) as transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions,
    RANK() OVER (PARTITION BY year, quarter ORDER BY SUM(transaction_count) DESC) as rank_by_volume
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2023
GROUP BY year, quarter, state
HAVING rank_by_volume <= 10
ORDER BY year DESC, quarter DESC, rank_by_volume;

-- 7.6 Most Diverse Payment Ecosystems
-- States with highest variety of transaction types
SELECT 
    state,
    COUNT(DISTINCT transaction_type) as payment_types_count,
    SUM(transaction_count) as total_transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount_billions,
    GROUP_CONCAT(DISTINCT transaction_type) as payment_types_available
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2022
GROUP BY state
ORDER BY payment_types_count DESC, total_transactions DESC
LIMIT 15;

-- 7.7 Transaction Type Leaders by State
-- Which transaction type dominates in each state?
WITH state_type_totals AS (
    SELECT 
        state,
        transaction_type,
        SUM(transaction_count) as type_transactions,
        SUM(transaction_amount) as type_amount
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2022
    GROUP BY state, transaction_type
),
state_ranks AS (
    SELECT 
        state,
        transaction_type,
        type_transactions,
        ROUND(type_amount / 1e9, 2) as amount_billions,
        ROW_NUMBER() OVER (PARTITION BY state ORDER BY type_transactions DESC) as rank
    FROM state_type_totals
)
SELECT 
    state,
    transaction_type as dominant_payment_type,
    type_transactions,
    amount_billions
FROM state_ranks
WHERE rank = 1
ORDER BY type_transactions DESC
LIMIT 20;

-- 7.8 Growth Momentum Rankings
-- States with strongest recent growth
WITH quarterly_performance AS (
    SELECT 
        state,
        year,
        quarter,
        SUM(transaction_count) as quarterly_trans
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2022
    GROUP BY state, year, quarter
),
growth_calc AS (
    SELECT 
        state,
        year,
        quarter,
        quarterly_trans,
        LAG(quarterly_trans) OVER (PARTITION BY state ORDER BY year, quarter) as prev_quarter,
        ROUND(
            (quarterly_trans - LAG(quarterly_trans) OVER (PARTITION BY state ORDER BY year, quarter)) * 100.0 /
            NULLIF(LAG(quarterly_trans) OVER (PARTITION BY state ORDER BY year, quarter), 0), 2
        ) as growth_pct
    FROM quarterly_performance
)
SELECT 
    state,
    AVG(growth_pct) as avg_quarterly_growth_pct,
    MAX(quarterly_trans) as peak_quarter_trans,
    MIN(quarterly_trans) as lowest_quarter_trans,
    COUNT(*) as quarters_with_data
FROM growth_calc
WHERE prev_quarter IS NOT NULL
GROUP BY state
ORDER BY avg_quarterly_growth_pct DESC
LIMIT 15;

-- 7.9 State Performance Scorecard
-- Comprehensive ranking across multiple metrics
WITH state_metrics AS (
    SELECT 
        state,
        SUM(transaction_count) as total_trans,
        ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount,
        ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_value,
        COUNT(DISTINCT transaction_type) as payment_diversity
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2022
    GROUP BY state
)
SELECT 
    state,
    total_trans,
    total_amount,
    avg_value,
    payment_diversity,
    RANK() OVER (ORDER BY total_trans DESC) as volume_rank,
    RANK() OVER (ORDER BY total_amount DESC) as value_rank,
    RANK() OVER (ORDER BY avg_value DESC) as ticket_rank,
    RANK() OVER (ORDER BY payment_diversity DESC) as diversity_rank,
    ROUND((
        RANK() OVER (ORDER BY total_trans DESC) +
        RANK() OVER (ORDER BY total_amount DESC) +
        RANK() OVER (ORDER BY avg_value DESC) +
        RANK() OVER (ORDER BY payment_diversity DESC)
    ) / 4.0, 1) as composite_score
FROM state_metrics
ORDER BY composite_score
LIMIT 20;

-- 7.10 Year-over-Year State Comparison
-- How states performed relative to previous year
WITH yearly_comparison AS (
    SELECT 
        state,
        year,
        SUM(transaction_count) as yearly_trans,
        SUM(transaction_amount) as yearly_amount
    FROM aggregated_transaction
    WHERE state != 'All India' AND year IN (2022, 2023)
    GROUP BY state, year
)
SELECT 
    state,
    MAX(CASE WHEN year = 2023 THEN yearly_trans END) as trans_2023,
    MAX(CASE WHEN year = 2022 THEN yearly_trans END) as trans_2022,
    ROUND(MAX(CASE WHEN year = 2023 THEN yearly_amount END) / 1e9, 2) as amount_2023_billions,
    ROUND(MAX(CASE WHEN year = 2022 THEN yearly_amount END) / 1e9, 2) as amount_2022_billions,
    ROUND(
        (MAX(CASE WHEN year = 2023 THEN yearly_trans END) - 
         MAX(CASE WHEN year = 2022 THEN yearly_trans END)) * 100.0 /
        NULLIF(MAX(CASE WHEN year = 2022 THEN yearly_trans END), 0), 2
    ) as yoy_growth_pct
FROM yearly_comparison
GROUP BY state
HAVING trans_2022 > 0 AND trans_2023 > 0
ORDER BY yoy_growth_pct DESC
LIMIT 20;
