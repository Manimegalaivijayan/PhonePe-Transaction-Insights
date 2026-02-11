# SQL Queries Documentation

This directory contains SQL queries for analyzing PhonePe Pulse data across 5 business cases.

## 📁 Query Files

### 1. **case_1_transaction_dynamics.sql**
**Business Case:** Decoding Transaction Dynamics on PhonePe

**Queries Included:**
- 1.1: Overall Transaction Trends (Year-over-Year Growth)
- 1.2: Transaction Type Performance  
- 1.3: Seasonal Pattern Analysis (Quarter-wise)
- 1.4: Transaction Type Growth by Year
- 1.5: States with Declining Transactions
- 1.6: Transaction Count vs Amount Correlation
- 1.7: Top Growing Transaction Types

**Key Insights:**
- Transaction growth rates
- Payment category performance
- Seasonal patterns
- Stagnant/declining markets

---

### 2. **case_2_device_engagement.sql**
**Business Case:** Device Dominance and User Engagement Analysis

**Queries Included:**
- 2.1: Device Brand Market Share
- 2.2: Engagement Rate by Device Brand
- 2.3: Device Brand Trends Over Time
- 2.4: Low Engagement Devices
- 2.5: Regional Device Preferences
- 2.6: Quarterly User Growth by Device
- 2.7: Device Brand Concentration Analysis
- 2.8: State-wise Engagement Comparison

**Key Insights:**
- Popular device brands
- User engagement patterns
- Regional preferences
- Market concentration

---

### 3. **case_4_market_expansion.sql**
**Business Case:** Transaction Analysis for Market Expansion

**Queries Included:**
- 4.1: Top States by Transaction Volume
- 4.2: Emerging Markets (High Growth States)
- 4.3: Market Penetration Index
- 4.4: Transaction Density by State
- 4.5: Untapped Potential States
- 4.6: Payment Type Diversity by State
- 4.7: Quarterly Momentum Analysis
- 4.8: State Ranking by Multiple Metrics

**Key Insights:**
- Market leaders
- Growth opportunities
- Expansion targets
- Market maturity levels

---

### 4. **case_5_user_engagement.sql**
**Business Case:** User Engagement and Growth Strategy

**Queries Included:**
- 5.1: User Growth Trends
- 5.2: State-wise User Engagement Rankings
- 5.3: User Retention Patterns
- 5.4: High Potential Growth States
- 5.5: App Usage Intensity Analysis
- 5.6: Quarterly Active User Growth
- 5.7: Engagement vs. User Base Correlation
- 5.8: User Acquisition Velocity
- 5.9: Engagement Consistency Score

**Key Insights:**
- User acquisition rates
- Retention metrics
- Engagement patterns
- Growth momentum

---

### 5. **case_7_state_district_analysis.sql**
**Business Case:** Transaction Analysis Across States and Districts

**Queries Included:**
- 7.1: Top 10 States by Transaction Volume
- 7.2: Top 10 States by Transaction Amount
- 7.3: Transaction Concentration Analysis
- 7.4: High-Value Transaction States
- 7.5: Quarterly Performance Leaders
- 7.6: Most Diverse Payment Ecosystems
- 7.7: Transaction Type Leaders by State
- 7.8: Growth Momentum Rankings
- 7.9: State Performance Scorecard
- 7.10: Year-over-Year State Comparison

**Key Insights:**
- Top performing states
- Market concentration
- Geographic trends
- Comparative performance

---

## 🔧 Usage

### Using Python Query Executor

```python
from src.analysis.query_executor import QueryExecutor

# Initialize executor
executor = QueryExecutor("data/phonepe_pulse.db")
executor.connect()

# Execute specific business case queries
case_1_results = executor.get_case_1_data()
case_2_results = executor.get_case_2_data()
case_4_results = executor.get_case_4_data()
case_5_results = executor.get_case_5_data()
case_7_results = executor.get_case_7_data()

# Execute custom query
df = executor.execute_query("SELECT * FROM aggregated_transaction LIMIT 10")

executor.disconnect()
```

### Using SQLite CLI

```bash
# Open database
sqlite3 data/phonepe_pulse.db

# Run a query file
.read sql/queries/case_1_transaction_dynamics.sql

# Or run individual queries
SELECT * FROM aggregated_transaction WHERE state = 'maharashtra' LIMIT 10;
```

---

## 📊 Sample Query Results

### Transaction Summary (2018-2024)
```
Year | Total Transactions | Amount (Billions)
-----|-------------------|------------------
2018 | 1.08B            | ₹1,623
2019 | 4.08B            | ₹6,277
2020 | 7.97B            | ₹14,641
2021 | 19.29B           | ₹34,599
2022 | 39.30B           | ₹64,267
2023 | 64.26B           | ₹94,492
2024 | 99.30B           | ₹129,625
```

### Top States by Volume (2022-2024)
```
State          | Transactions | Amount (Billions)
---------------|-------------|------------------
maharashtra    | 27.35B      | ₹33,449
karnataka      | 26.30B      | ₹33,809
telangana      | 22.43B      | ₹34,440
uttar-pradesh  | 16.50B      | ₹23,154
andhra-pradesh | 16.18B      | ₹28,668
```

### Transaction Types Performance
```
Type                      | Transactions | Amount (Billions)
-------------------------|-------------|------------------
Peer-to-peer payments    | 85.03B      | ₹266,529
Merchant payments        | 130.24B     | ₹65,340
Recharge & bill payments | 19.60B      | ₹13,339
Financial Services       | 154M        | ₹142
Others                   | 262M        | ₹174
```

---

## 💡 Query Optimization Tips

1. **Use Indexes**: The database has indexes on frequently queried columns (state, year, quarter)
2. **Filter Early**: Use WHERE clauses to reduce data before aggregation
3. **Limit Results**: Add LIMIT for testing queries
4. **Window Functions**: Used for growth calculations and rankings
5. **CTEs**: Common Table Expressions improve query readability

---

## 🔍 Common Query Patterns

### Year-over-Year Growth
```sql
SELECT 
    year,
    SUM(metric) as total,
    LAG(SUM(metric)) OVER (ORDER BY year) as prev_year,
    ROUND(
        (SUM(metric) - LAG(SUM(metric)) OVER (ORDER BY year)) * 100.0 /
        NULLIF(LAG(SUM(metric)) OVER (ORDER BY year), 0), 2
    ) as growth_pct
FROM table
GROUP BY year;
```

### Top N Rankings
```sql
SELECT *
FROM (
    SELECT *, RANK() OVER (ORDER BY metric DESC) as rank
    FROM aggregated_data
)
WHERE rank <= 10;
```

### Market Share Calculation
```sql
SELECT 
    category,
    metric,
    ROUND(metric * 100.0 / SUM(metric) OVER (), 2) as market_share_pct
FROM data;
```

---

## 📈 Next Steps

1. **Visualizations**: Use these queries in Streamlit dashboard
2. **Exports**: Generate CSV/Excel reports
3. **Automation**: Schedule regular query execution
4. **Alerts**: Set up notifications for anomalies
5. **ML Models**: Use query results for predictive analytics

---

**Last Updated:** February 10, 2026
