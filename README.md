# PhonePe Transaction Insights
<img width="1916" height="964" alt="image" src="https://github.com/user-attachments/assets/85f9b7b6-96e0-471c-a3b0-bfd93dd1e869" />

A comprehensive analytics platform for PhonePe transaction data. This project provides interactive visualizations and deep-dive analysis into digital payment patterns, device engagement, user trends, and market expansion opportunities across India.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Business Cases](#business-cases)
- [Chart Purpose & Outcomes](#-chart-purpose--outcomes)
- [Technologies Used](#technologies-used)

## 🎯 Project Overview

This project analyzes PhonePe Pulse data to provide actionable insights into:
- **Transaction Dynamics**: Year-over-year trends, payment category performance, and growth patterns
- **Device Engagement**: Device brand preferences and regional market share distribution
- **Market Expansion**: High-performing states and emerging market opportunities
- **User Growth**: User engagement trends and retention patterns
- **State & District Analysis**: Deep dive into transaction performance across regions

## ✨ Features

- **Interactive Dashboard**: Real-time data visualization with Streamlit
- **Multiple Business Cases**: Comprehensive analysis modules for different perspectives
- **Geographic Analysis**: State and district-level heatmaps and comparisons
- **Trend Analysis**: Year-over-year and quarterly performance tracking
- **Device Analytics**: Brand preference and market share insights
- **Filter Options**: Dynamic filtering by year, quarter, and state

## 📁 Project Structure

```
PhonePe-Transaction-Insights/
│
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── test.py                           # Testing utilities
│
├── config/
│   ├── config.yaml                   # Configuration file (template)
│   └── config.yaml.example           # Example configuration
│
├── data/                             # Data storage directory
│   └── raw/
│       └── pulse/                    # PhonePe Pulse data
│           ├── LICENSE               # Data license
│           ├── README.md             # Data documentation
│           └── data/
│               ├── aggregated/       # Pre-aggregated data
│               │   ├── insurance/    # Insurance metrics
│               │   ├── transaction/  # Transaction data
│               │   └── user/         # User metrics
│               ├── map/              # Geographic mapping data
│               │   ├── insurance/
│               │   ├── transaction/
│               │   └── user/
│               └── top/              # Top performers data
│                   ├── insurance/
│                   ├── transaction/
│                   └── user/
│
├── sql/                              # SQL queries and scripts
│   ├── schema_sqlite.sql            # Database schema definition
│   └── queries/                      # Business logic queries
│       ├── case_1_transaction_dynamics.sql
│       ├── case_2_device_engagement.sql
│       ├── case_4_market_expansion.sql
│       ├── case_5_user_engagement.sql
│       ├── case_7_state_district_analysis.sql
│       └── README.md
│
└── src/                              # Source code
    ├── analysis/                     # Data analysis modules
    │   ├── query_executor_simple.py # SQL query executor
    │   └── __pycache__/
    │
    ├── dashboard/                    # Streamlit dashboard
    │   ├── __init__.py
    │   ├── app.py                   # Main Streamlit application
    │   ├── business_cases.py        # Business case definitions
    │   ├── map_utils.py             # Geographic visualization utilities
    │   └── __pycache__/
    │
    └── etl/                          # Extract, Transform, Load
        ├── __init__.py
        ├── extractor_simple.py      # Data extraction logic
        ├── loader_simple.py         # Data loading logic
        ├── main_simple.py           # ETL orchestration
        └── __pycache__/
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip or conda
- SQLite3 (included with Python)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Manimegalaivijayan/PhonePe-Transaction-Insights.git
cd PhonePe-Transaction-Insights
```

### Step 2: Create Virtual Environment
```bash
# Using venv
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Settings (Optional)
```bash
# Copy example config
cp config/config.yaml.example config/config.yaml

# Edit config.yaml with your preferences
```

## 💻 Usage

### Running the Dashboard

```bash
# Make sure virtual environment is activated
streamlit run src/dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### Dashboard Navigation

1. **Home Page**: Overview with key performance indicators (KPIs) and summary statistics
2. **Business Cases**: Navigate between 5 different analysis modules:
   - **Case 1**: Transaction Dynamics - Payment patterns and growth trends
   - **Case 2**: Device Engagement - Brand preferences and market share
   - **Case 4**: Market Expansion - High-growth states and opportunities
   - **Case 5**: User Engagement - Growth trends and retention patterns
   - **Case 7**: State & District Analysis - Regional performance comparison

### Filtering Data

Use the sidebar filters to customize your analysis:
- **Year**: Select specific year (2018-2024) or view all years
- **Quarter**: Q1-Q4 or all quarters
- **State**: Choose individual state or "All India"

## 📊 Data Sources

The project uses PhonePe Pulse data containing:

### Transaction Data
- Transaction volume and amount by type
- Payment method preferences
- Geographic distribution
- Temporal trends

### User Data
- Active user counts
- Device brand distribution
- Regional user demographics
- Growth trends

### Insurance Data
- Insurance premium metrics
- Policy distribution
- Regional coverage

Data is organized by:
- **Aggregated**: Pre-summed metrics for quick access
- **Map**: Geographic coordinates for choropleth visualizations
- **Top**: Top 10 performers by various metrics

## 🎨 Business Cases

### Case 1: Decoding Transaction Dynamics
Analyzes transaction patterns, growth trends, and payment category performance.

**Key Questions:**
- What are the year-over-year transaction growth rates?
- Which transaction types drive the highest value?
- Are there seasonal patterns in digital payments?
- Which states show declining transaction trends?

### Case 2: Device Dominance & User Engagement
Examines device brand preferences and market share distribution.

**Key Questions:**
- Which device brands dominate the digital payment market?
- How does device preference vary by region?
- What is the relationship between device brand and user engagement?

### Case 4: Transaction Analysis for Market Expansion
Identifies high-performing states and expansion opportunities.

**Key Questions:**
- Which states have the highest transaction volumes?
- Where are the emerging high-growth markets?
- What is the digital payment penetration by state?

### Case 5: User Engagement and Growth Strategy
Analyzes user growth trends and engagement metrics.

**Key Questions:**
- What are the user growth trends?
- Which states have the highest user engagement?
- What factors drive consistent user engagement?

### Case 7: State & District Analysis
Deep dive into state and district-level performance.

**Key Questions:**
- Which are the top 10 states by transaction volume?
- How concentrated is transaction activity?
- How do year-over-year comparisons look across states?

## 📊 Chart Purpose & Outcomes

This section explains why each chart in the dashboard is used and what decision outcome it supports.

### Home Page

| Chart | Why this chart is used | Outcome it serves |
|---|---|---|
| Total Transactions by Year (line) | Shows trajectory of transaction adoption over time | Quickly identifies long-term momentum and acceleration/slowdown periods |
| Transaction Amount by Year (bar) | Highlights value growth trend in currency terms | Helps estimate market value expansion and monetization potential |
| India Choropleth (Transactions/Amount) | Compares state-level intensity geographically | Supports regional prioritization and territory strategy |
| Top 15 States by Transaction Volume | Ranks strongest states by activity | Identifies core operating markets |
| Top 15 States by Transaction Amount | Ranks strongest states by value | Identifies high-value markets, not just high-volume ones |

### Case 1: Decoding Transaction Dynamics

| Chart | Why this chart is used | Outcome it serves |
|---|---|---|
| Transaction Volume vs Amount by Type (bubble/scatter) | Compares volume, value, and ticket size simultaneously by transaction type | Identifies categories that are high-frequency vs high-value |
| Average Ticket Size by Transaction Type (bar) | Normalizes value per transaction across types | Helps optimize category-level pricing, incentives, and product focus |
| YoY Growth Rate by Transaction Type (bar) | Compares category growth strength for a selected year context | Surfaces expanding vs weakening transaction types |
| Average Transactions by Quarter (bar) | Captures seasonal usage pattern | Helps plan campaigns and capacity for seasonal spikes |
| Transaction Distribution by Type (donut/pie) | Shows composition split across transaction types | Supports portfolio balancing and category concentration checks |
| Average Transaction Amount by Quarter (line) | Tracks seasonal changes in ticket value | Informs quarter-wise revenue expectations |
| Average Amount by Transaction Type (bar) | Compares value intensity across categories | Guides which categories drive larger per-transaction economics |
| Transaction Type Distribution Across Top 15 States (stacked bar) | Shows full mix of payment types by state | Enables state-specific product and GTM customization |
| All States YoY Growth (all-state bar, red/green) | Shows complete state performance with declines and growth together | Gives balanced performance review instead of decline-only view |
| Year-wise Growth Pattern (Declining States heatmap) | Shows multi-year decline/recovery pattern for decline-prone states | Supports risk monitoring and turnaround planning |

### Case 2: Device Dominance & User Engagement

| Chart | Why this chart is used | Outcome it serves |
|---|---|---|
| Top 10 Device Brands by User Base (donut/pie) | Displays market concentration among top brands | Highlights ecosystem dependency risk/opportunity |
| Market Share % by Brand (bar) | Provides direct comparative brand share percentages | Supports partnership and device-priority decisions |
| Top 8 Device Brands – User Growth Over Time (line) | Tracks brand adoption trend by year | Detects emerging brands and declining incumbents |
| Device Preference by Region (Top 5 Brands across Top 10 States, grouped bar) | Shows multi-brand regional preference instead of single winner | Enables region-wise brand targeting strategy |
| Brand Diversity vs User Base (scatter) | Compares market size vs brand variety | Identifies concentrated vs competitive state ecosystems |
| Top 10 States by Registered Users (bar) | Ranks states by user depth | Supports market sizing and expansion sequencing |

### Case 4: Market Expansion

| Chart | Why this chart is used | Outcome it serves |
|---|---|---|
| Quarterly Transaction Volume (bar) | Tracks near-term movement of transaction activity | Supports quarter-level execution planning |
| Quarter-over-Quarter Growth Rate (line) | Shows short-term growth trend and reversals | Early warning for slowdown or recovery |
| Emerging Markets: High Growth + Moderate Volume (scatter) | Identifies high-growth but not saturated states | Prioritizes expansion candidates |
| Top Emerging Markets (rank cards) | Provides simple ranked shortlist with growth | Quick decision support for leadership reviews |
| Top 10 High-Volume States (bar) | Highlights established core markets | Distinguishes mature states from emerging targets |
| High Engagement, Moderate Volume States (bar) | Captures underpenetrated but active markets | Finds high-upside expansion opportunities |
| User Base vs Transaction Volume (bubble) | Relates demand base to transaction output with engagement proxy | Helps identify penetration gaps |

### Case 5: User Engagement & Growth Strategy

| Chart | Why this chart is used | Outcome it serves |
|---|---|---|
| Top 15 States by User Growth Rate (bar) | Ranks state-level user growth strength | Reveals where user acquisition/retention momentum is strongest |
| States with Consistent User Growth (bar, positive years) | Rewards consistency, not just one-time spikes | Finds sustainable growth markets |
| Highest User Engagement States (bar) | Ranks states by total registered users | Identifies strong user-base anchors |
| Fastest Growing States (bar) | Focuses on latest YoY user acceleration | Supports near-term growth bets |

### Case 7: State & District Analysis

| Chart | Why this chart is used | Outcome it serves |
|---|---|---|
| Top 10 States Performance Dashboard (cards) | Combines rank, volume, value, and share in one view | Fast executive snapshot of top-state performance |
| Top 10 States: Transaction Volume vs Value (scatter) | Compares throughput vs value with share context | Distinguishes states that are high-volume, high-value, or outliers |
| Transaction Concentration (Pareto Analysis) | Measures concentration of total activity across states | Shows whether business is concentrated in few states or broadly distributed |
| District-Level Analysis (state drill-down bars) | Breaks selected top states into district detail | Supports hyperlocal planning and resource allocation |

## 🛠 Technologies Used

### Data Processing & Analysis
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **SQLite3**: Database management

### Visualization
- **Streamlit**: Interactive web dashboard framework
- **Plotly**: Interactive charts and graphs
- **Matplotlib & Seaborn**: Statistical visualizations

### ETL & Infrastructure
- **GitPython**: Version control integration
- **python-dotenv**: Environment variable management
- **PyYAML**: Configuration file handling
- **tqdm**: Progress tracking

### Development Tools
- **Jupyter**: Interactive notebooks for exploration
- **IPython**: Enhanced Python shell

## 📝 Configuration

Edit `config/config.yaml` to customize:
- Database paths
- Data sources
- Visualization preferences
- Filter defaults

Example:
```yaml
database:
  path: "./data/phonepe_pulse.db"

visualization:
  theme: "light"
  colors: "default"
```

## 📦 Requirements

See [requirements.txt](requirements.txt) for complete list. Key packages:
- streamlit==1.54.0
- plotly==5.18.0
- pandas==2.3.3
- numpy==2.4.2
- sqlite3 (built-in)

## 🔄 ETL Process

The project includes ETL modules for data integration:

1. **Extractor** (`src/etl/extractor_simple.py`): Fetches data from PhonePe Pulse
2. **Loader** (`src/etl/loader_simple.py`): Processes and stores data in SQLite
3. **Main** (`src/etl/main_simple.py`): Orchestrates the ETL pipeline

## 📚 Database Schema

Database schema is defined in `sql/schema_sqlite.sql` with tables for:
- `aggregated_transaction`: Transaction metrics
- `aggregated_user`: User metrics
- `aggregated_insurance`: Insurance metrics

See [SQL README](sql/README.md) for detailed schema documentation.

## 👤 Author

**Manimegalai V**

**Last Updated**: February 2026
