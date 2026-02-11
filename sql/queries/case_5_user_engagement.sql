-- ============================================
-- BUSINESS CASE 5: User Engagement and Growth Strategy
-- ============================================
-- Analyzing user engagement for strategic decision-making

-- 5.1 User Growth Trends
-- Overall user registration and app usage trends
SELECT 
    year,
    quarter,
    registered_users,
    app_opens,
    ROUND(CAST(app_opens AS FLOAT) / NULLIF(registered_users, 0), 2) as engagement_rate,
    LAG(registered_users) OVER (ORDER BY year, quarter) as prev_quarter_users,
    ROUND(
        (registered_users - LAG(registered_users) OVER (ORDER BY year, quarter)) * 100.0 /
        NULLIF(LAG(registered_users) OVER (ORDER BY year, quarter), 0), 2
    ) as user_growth_pct
FROM aggregated_user
WHERE state = 'All India' AND brand = 'Total'
ORDER BY year, quarter;

-- 5.2 State-wise User Engagement Rankings
-- Identifies states with highest and lowest engagement
SELECT 
    state,
    SUM(registered_users) as total_users,
    SUM(app_opens) as total_opens,
    ROUND(CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0), 2) as engagement_score,
    RANK() OVER (ORDER BY CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0) DESC) as engagement_rank
FROM aggregated_user
WHERE state != 'All India' AND brand = 'Total' AND year >= 2022
GROUP BY state
ORDER BY engagement_score DESC;

-- 5.3 User Retention Patterns
-- Tracks if users continue to use the app over quarters
WITH quarterly_users AS (
    SELECT 
        state,
        year,
        quarter,
        registered_users,
        app_opens,
        LAG(app_opens) OVER (PARTITION BY state ORDER BY year, quarter) as prev_quarter_opens
    FROM aggregated_user
    WHERE brand = 'Total' AND year >= 2022
)
SELECT 
    state,
    year,
    quarter,
    registered_users,
    app_opens,
    prev_quarter_opens,
    ROUND((app_opens - prev_quarter_opens) * 100.0 / NULLIF(prev_quarter_opens, 0), 2) as retention_change_pct,
    CASE 
        WHEN app_opens > prev_quarter_opens THEN 'Growing'
        WHEN app_opens < prev_quarter_opens THEN 'Declining'
        ELSE 'Stable'
    END as retention_trend
FROM quarterly_users
WHERE state = 'All India' AND prev_quarter_opens IS NOT NULL
ORDER BY year DESC, quarter DESC;

-- 5.4 High Potential Growth States
-- States with growing user base
WITH state_growth AS (
    SELECT 
        state,
        year,
        SUM(registered_users) as yearly_users,
        SUM(app_opens) as yearly_opens
    FROM aggregated_user
    WHERE state != 'All India' AND brand = 'Total'
    GROUP BY state, year
)
SELECT 
    state,
    MAX(CASE WHEN year = 2023 THEN yearly_users END) as users_2023,
    MAX(CASE WHEN year = 2022 THEN yearly_users END) as users_2022,
    MAX(CASE WHEN year = 2021 THEN yearly_users END) as users_2021,
    ROUND(
        (MAX(CASE WHEN year = 2023 THEN yearly_users END) - 
         MAX(CASE WHEN year = 2022 THEN yearly_users END)) * 100.0 /
        NULLIF(MAX(CASE WHEN year = 2022 THEN yearly_users END), 0), 2
    ) as growth_2023_pct,
    MAX(CASE WHEN year = 2023 THEN yearly_opens END) as opens_2023
FROM state_growth
WHERE year IN (2021, 2022, 2023)
GROUP BY state
HAVING MAX(CASE WHEN year = 2023 THEN yearly_users END) IS NOT NULL
ORDER BY growth_2023_pct DESC
LIMIT 15;

-- 5.5 App Usage Intensity Analysis
-- Average app opens per user (frequency of usage)
SELECT 
    state,
    year,
    quarter,
    registered_users,
    app_opens,
    ROUND(CAST(app_opens AS FLOAT) / NULLIF(registered_users, 0), 2) as avg_opens_per_user,
    CASE 
        WHEN CAST(app_opens AS FLOAT) / NULLIF(registered_users, 0) > 50 THEN 'Very High Usage'
        WHEN CAST(app_opens AS FLOAT) / NULLIF(registered_users, 0) > 30 THEN 'High Usage'
        WHEN CAST(app_opens AS FLOAT) / NULLIF(registered_users, 0) > 15 THEN 'Medium Usage'
        ELSE 'Low Usage'
    END as usage_category
FROM aggregated_user
WHERE state != 'All India' AND brand = 'Total' AND year >= 2022
ORDER BY avg_opens_per_user DESC
LIMIT 20;

-- 5.6 Quarterly Active User Growth
-- Net new users per quarter
WITH quarterly_change AS (
    SELECT 
        state,
        year,
        quarter,
        registered_users,
        LAG(registered_users) OVER (PARTITION BY state ORDER BY year, quarter) as prev_users
    FROM aggregated_user
    WHERE brand = 'Total' AND year >= 2021
)
SELECT 
    state,
    year,
    quarter,
    registered_users,
    prev_users,
    (registered_users - prev_users) as net_new_users,
    ROUND((registered_users - prev_users) * 100.0 / NULLIF(prev_users, 0), 2) as growth_pct
FROM quarterly_change
WHERE state = 'All India' AND prev_users IS NOT NULL
ORDER BY year DESC, quarter DESC;

-- 5.7 Engagement vs. User Base Correlation
-- Do states with more users have better engagement?
WITH state_metrics AS (
    SELECT 
        state,
        SUM(registered_users) as total_users,
        SUM(app_opens) as total_opens,
        ROUND(CAST(SUM(app_opens) AS FLOAT) / NULLIF(SUM(registered_users), 0), 2) as engagement_rate
    FROM aggregated_user
    WHERE state != 'All India' AND brand = 'Total' AND year >= 2022
    GROUP BY state
)
SELECT 
    CASE 
        WHEN total_users > 50000000 THEN 'Very Large'
        WHEN total_users > 20000000 THEN 'Large'
        WHEN total_users > 10000000 THEN 'Medium'
        ELSE 'Small'
    END as market_size,
    COUNT(*) as state_count,
    ROUND(AVG(engagement_rate), 2) as avg_engagement,
    MIN(engagement_rate) as min_engagement,
    MAX(engagement_rate) as max_engagement
FROM state_metrics
GROUP BY market_size
ORDER BY 
    CASE market_size
        WHEN 'Very Large' THEN 1
        WHEN 'Large' THEN 2
        WHEN 'Medium' THEN 3
        ELSE 4
    END;

-- 5.8 User Acquisition Velocity
-- Rate of user acquisition by state and period
WITH user_velocity AS (
    SELECT 
        state,
        year,
        quarter,
        registered_users,
        LAG(registered_users, 1) OVER (PARTITION BY state ORDER BY year, quarter) as prev_1q,
        LAG(registered_users, 2) OVER (PARTITION BY state ORDER BY year, quarter) as prev_2q,
        LAG(registered_users, 3) OVER (PARTITION BY state ORDER BY year, quarter) as prev_3q
    FROM aggregated_user
    WHERE brand = 'Total' AND year >= 2022
)
SELECT 
    state,
    year,
    quarter,
    registered_users,
    (registered_users - prev_1q) as growth_1q,
    (registered_users - prev_2q) as growth_2q,
    (registered_users - prev_3q) as growth_3q,
    ROUND((registered_users - prev_1q) * 100.0 / NULLIF(prev_1q, 0), 2) as growth_pct_1q
FROM user_velocity
WHERE state != 'All India' AND prev_3q IS NOT NULL
ORDER BY growth_pct_1q DESC
LIMIT 20;

-- 5.9 Engagement Consistency Score
-- States with stable, consistent engagement
WITH engagement_history AS (
    SELECT 
        state,
        year,
        quarter,
        ROUND(CAST(app_opens AS FLOAT) / NULLIF(registered_users, 0), 2) as engagement_rate
    FROM aggregated_user
    WHERE state != 'All India' AND brand = 'Total' AND year >= 2022
)
SELECT 
    state,
    COUNT(*) as quarters_measured,
    ROUND(AVG(engagement_rate), 2) as avg_engagement,
    ROUND(MIN(engagement_rate), 2) as min_engagement,
    ROUND(MAX(engagement_rate), 2) as max_engagement,
    ROUND(MAX(engagement_rate) - MIN(engagement_rate), 2) as engagement_volatility,
    CASE 
        WHEN MAX(engagement_rate) - MIN(engagement_rate) < 5 THEN 'Very Consistent'
        WHEN MAX(engagement_rate) - MIN(engagement_rate) < 10 THEN 'Consistent'
        ELSE 'Variable'
    END as consistency_rating
FROM engagement_history
GROUP BY state
HAVING quarters_measured >= 4
ORDER BY engagement_volatility ASC
LIMIT 20;
