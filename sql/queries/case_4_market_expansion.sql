-- ============================================
-- BUSINESS CASE 4: Transaction Analysis for Market Expansion
-- ============================================
-- Strategic decision-making for identifying expansion opportunities

-- 4.1 Top States by Transaction Volume
-- Identifies leading markets
SELECT 
    state,
    SUM(transaction_count) as total_transactions,
    ROUND(SUM(transaction_amount) / 1e9, 2) as total_amount_billions,
    ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_transaction_value,
    COUNT(DISTINCT transaction_type) as payment_types_used
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2022
GROUP BY state
ORDER BY total_amount_billions DESC
LIMIT 15;

-- 4.2 Emerging Markets (High Growth States)
-- Identifies states with significant growth potential
WITH state_yearly AS (
    SELECT 
        state,
        year,
        SUM(transaction_count) as yearly_transactions,
        SUM(transaction_amount) as yearly_amount
    FROM aggregated_transaction
    WHERE state != 'All India'
    GROUP BY state, year
)
SELECT 
    state,
    MAX(CASE WHEN year = 2023 THEN yearly_transactions END) as trans_2023,
    MAX(CASE WHEN year = 2022 THEN yearly_transactions END) as trans_2022,
    MAX(CASE WHEN year = 2021 THEN yearly_transactions END) as trans_2021,
    ROUND(
        (MAX(CASE WHEN year = 2023 THEN yearly_transactions END) - 
         MAX(CASE WHEN year = 2022 THEN yearly_transactions END)) * 100.0 /
        NULLIF(MAX(CASE WHEN year = 2022 THEN yearly_transactions END), 0), 2
    ) as growth_2023_pct,
    ROUND(
        (MAX(CASE WHEN year = 2022 THEN yearly_transactions END) - 
         MAX(CASE WHEN year = 2021 THEN yearly_transactions END)) * 100.0 /
        NULLIF(MAX(CASE WHEN year = 2021 THEN yearly_transactions END), 0), 2
    ) as growth_2022_pct
FROM state_yearly
WHERE year IN (2021, 2022, 2023)
GROUP BY state
HAVING MAX(CASE WHEN year = 2023 THEN yearly_transactions END) IS NOT NULL
ORDER BY growth_2023_pct DESC
LIMIT 15;

-- 4.3 Market Penetration Index
-- Combines volume and value for market assessment
WITH state_metrics AS (
    SELECT 
        state,
        SUM(transaction_count) as total_trans,
        SUM(transaction_amount) as total_amount,
        COUNT(DISTINCT year || '-' || quarter) as quarters_active
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2021
    GROUP BY state
)
SELECT 
    state,
    total_trans,
    ROUND(total_amount / 1e9, 2) as amount_billions,
    quarters_active,
    ROUND((total_trans * total_amount / 1e18), 2) as penetration_index,
    CASE 
        WHEN total_trans > 10000000000 AND total_amount > 10000000000000 THEN 'High Penetration'
        WHEN total_trans > 5000000000 AND total_amount > 5000000000000 THEN 'Medium Penetration'
        ELSE 'Low Penetration'
    END as market_maturity
FROM state_metrics
ORDER BY penetration_index DESC;

-- 4.4 Transaction Density by State
-- Average transactions per quarter (indicates market activity)
SELECT 
    state,
    COUNT(DISTINCT year || '-' || quarter) as total_quarters,
    SUM(transaction_count) as total_transactions,
    ROUND(CAST(SUM(transaction_count) AS FLOAT) / COUNT(DISTINCT year || '-' || quarter), 0) as avg_trans_per_quarter,
    ROUND(SUM(transaction_amount) / COUNT(DISTINCT year || '-' || quarter) / 1e9, 2) as avg_amount_per_quarter_billions
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2021
GROUP BY state
ORDER BY avg_trans_per_quarter DESC
LIMIT 20;

-- 4.5 Untapped Potential States
-- States with low current volume but growth indicators
WITH state_potential AS (
    SELECT 
        state,
        SUM(CASE WHEN year = 2023 THEN transaction_count ELSE 0 END) as trans_2023,
        SUM(CASE WHEN year = 2022 THEN transaction_count ELSE 0 END) as trans_2022,
        SUM(transaction_amount) as total_amount
    FROM aggregated_transaction
    WHERE state != 'All India' AND year IN (2022, 2023)
    GROUP BY state
)
SELECT 
    state,
    trans_2023,
    trans_2022,
    ROUND(total_amount / 1e9, 2) as total_amount_billions,
    ROUND((trans_2023 - trans_2022) * 100.0 / NULLIF(trans_2022, 0), 2) as growth_rate,
    CASE 
        WHEN trans_2023 < 5000000000 AND (trans_2023 - trans_2022) * 100.0 / NULLIF(trans_2022, 0) > 20 
        THEN 'High Potential'
        WHEN trans_2023 < 5000000000 THEN 'Untapped'
        ELSE 'Established'
    END as market_classification
FROM state_potential
WHERE trans_2022 > 0
ORDER BY growth_rate DESC;

-- 4.6 Payment Type Diversity by State
-- States with diverse payment adoption indicate market maturity
SELECT 
    state,
    COUNT(DISTINCT transaction_type) as payment_types,
    SUM(transaction_count) as total_transactions,
    GROUP_CONCAT(DISTINCT transaction_type) as available_types
FROM aggregated_transaction
WHERE state != 'All India' AND year >= 2022
GROUP BY state
ORDER BY payment_types DESC, total_transactions DESC
LIMIT 20;

-- 4.7 Quarterly Momentum Analysis
-- Identifies states with consistent growth momentum
WITH quarterly_growth AS (
    SELECT 
        state,
        year,
        quarter,
        SUM(transaction_count) as trans_count,
        LAG(SUM(transaction_count)) OVER (PARTITION BY state ORDER BY year, quarter) as prev_quarter
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2022
    GROUP BY state, year, quarter
)
SELECT 
    state,
    COUNT(*) as quarters_tracked,
    SUM(CASE WHEN trans_count > prev_quarter THEN 1 ELSE 0 END) as growth_quarters,
    ROUND(SUM(CASE WHEN trans_count > prev_quarter THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as consistency_score,
    MAX(trans_count) as peak_quarter_transactions
FROM quarterly_growth
WHERE prev_quarter IS NOT NULL
GROUP BY state
HAVING quarters_tracked >= 4
ORDER BY consistency_score DESC, peak_quarter_transactions DESC
LIMIT 15;

-- 4.8 State Ranking by Multiple Metrics
-- Comprehensive state performance scorecard
WITH state_scores AS (
    SELECT 
        state,
        SUM(transaction_count) as total_trans,
        SUM(transaction_amount) as total_amount,
        ROUND(AVG(transaction_amount / NULLIF(transaction_count, 0)), 2) as avg_value
    FROM aggregated_transaction
    WHERE state != 'All India' AND year >= 2022
    GROUP BY state
),
rankings AS (
    SELECT 
        state,
        total_trans,
        ROUND(total_amount / 1e9, 2) as amount_billions,
        avg_value,
        RANK() OVER (ORDER BY total_trans DESC) as volume_rank,
        RANK() OVER (ORDER BY total_amount DESC) as value_rank,
        RANK() OVER (ORDER BY avg_value DESC) as ticket_size_rank
    FROM state_scores
)
SELECT 
    state,
    volume_rank,
    value_rank,
    ticket_size_rank,
    ROUND((volume_rank + value_rank + ticket_size_rank) / 3.0, 1) as composite_rank,
    total_trans,
    amount_billions,
    avg_value
FROM rankings
ORDER BY composite_rank
LIMIT 20;
