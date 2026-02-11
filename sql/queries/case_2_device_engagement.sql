-- ============================================
-- BUSINESS CASE 2: Device Dominance & User Engagement
-- ============================================
-- Understanding user preferences across device brands to enhance engagement

-- 2.1 Device Brand Market Share
-- Shows which device brands have the highest user base
SELECT 
    brand,
    SUM(registered_users) as total_users,
    SUM(app_opens) as total_app_opens,
    ROUND(AVG(percentage) * 100, 2) as avg_market_share_pct,
    COUNT(DISTINCT year || '-' || quarter) as quarters_present
FROM aggregated_user
WHERE state = 'All India' AND brand != 'Total'
GROUP BY brand
ORDER BY total_users DESC;

-- 2.2 Engagement Rate by Device Brand
-- Calculates app opens per user (engagement metric)
SELECT 
    brand,
    SUM(registered_users) as total_users,
    SUM(app_opens) as total_app_opens,
    ROUND(CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0), 2) as engagement_rate,
    ROUND(SUM(app_opens) / 1e6, 2) as app_opens_millions
FROM aggregated_user
WHERE state = 'All India' AND brand != 'Total' AND brand IS NOT NULL
GROUP BY brand
HAVING SUM(registered_users) > 0
ORDER BY engagement_rate DESC;

-- 2.3 Device Brand Trends Over Time
-- Shows how device preferences are changing
SELECT 
    year,
    quarter,
    brand,
    registered_users,
    app_opens,
    ROUND(percentage * 100, 2) as market_share_pct
FROM aggregated_user
WHERE state = 'All India' AND brand != 'Total' AND year >= 2021
ORDER BY year DESC, quarter DESC, registered_users DESC
LIMIT 50;

-- 2.4 Low Engagement Devices (High Registration, Low App Opens)
-- Identifies devices with poor engagement despite high user base
WITH engagement_metrics AS (
    SELECT 
        brand,
        SUM(registered_users) as total_users,
        SUM(app_opens) as total_opens,
        ROUND(CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0), 2) as engagement_rate
    FROM aggregated_user
    WHERE state = 'All India' AND brand != 'Total'
    GROUP BY brand
)
SELECT 
    brand,
    total_users,
    total_opens,
    engagement_rate,
    CASE 
        WHEN engagement_rate < 10 THEN 'Very Low'
        WHEN engagement_rate < 20 THEN 'Low'
        WHEN engagement_rate < 30 THEN 'Medium'
        ELSE 'High'
    END as engagement_category
FROM engagement_metrics
WHERE total_users > 1000000  -- At least 1M users
ORDER BY engagement_rate ASC;

-- 2.5 Regional Device Preferences (Top 10 States)
-- Shows device preferences by state
SELECT 
    state,
    brand,
    SUM(registered_users) as users,
    ROUND(AVG(percentage) * 100, 2) as avg_share_pct
FROM aggregated_user
WHERE state != 'All India' AND brand != 'Total' AND year >= 2022
GROUP BY state, brand
HAVING SUM(registered_users) > 100000
ORDER BY state, users DESC;

-- 2.6 Quarterly User Growth by Device
-- Tracks user growth for each device brand
WITH quarterly_users AS (
    SELECT 
        brand,
        year,
        quarter,
        SUM(registered_users) as users
    FROM aggregated_user
    WHERE state = 'All India' AND brand != 'Total'
    GROUP BY brand, year, quarter
)
SELECT 
    brand,
    year,
    quarter,
    users,
    LAG(users) OVER (PARTITION BY brand ORDER BY year, quarter) as prev_quarter_users,
    ROUND(
        (users - LAG(users) OVER (PARTITION BY brand ORDER BY year, quarter)) * 100.0 /
        NULLIF(LAG(users) OVER (PARTITION BY brand ORDER BY year, quarter), 0), 2
    ) as growth_pct
FROM quarterly_users
WHERE year >= 2022
ORDER BY brand, year DESC, quarter DESC;

-- 2.7 Device Brand Concentration Analysis
-- Shows if market is dominated by few brands or distributed
WITH brand_stats AS (
    SELECT 
        brand,
        SUM(registered_users) as total_users,
        (SELECT SUM(registered_users) FROM aggregated_user WHERE state = 'All India' AND brand != 'Total') as grand_total
    FROM aggregated_user
    WHERE state = 'All India' AND brand != 'Total'
    GROUP BY brand
)
SELECT 
    brand,
    total_users,
    ROUND(total_users * 100.0 / grand_total, 2) as market_share_pct,
    SUM(ROUND(total_users * 100.0 / grand_total, 2)) OVER (ORDER BY total_users DESC) as cumulative_share_pct
FROM brand_stats
ORDER BY total_users DESC;

-- 2.8 State-wise Engagement Comparison
-- Identifies states with highest/lowest engagement
SELECT 
    state,
    SUM(registered_users) as total_users,
    SUM(app_opens) as total_opens,
    ROUND(CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0), 2) as engagement_rate
FROM aggregated_user
WHERE state != 'All India' AND brand = 'Total' AND year >= 2022
GROUP BY state
HAVING SUM(registered_users) > 0
ORDER BY engagement_rate DESC
LIMIT 20;
