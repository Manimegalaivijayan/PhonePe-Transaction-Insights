# PhonePe Transaction Insights

A comprehensive analytics platform for PhonePe transaction data. This project provides interactive visualizations and deep-dive analysis into digital payment patterns, device engagement, user trends, and market expansion opportunities across India.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Business Cases](#business-cases)
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project uses PhonePe Pulse data. See [LICENSE](data/raw/pulse/LICENSE) for data usage terms.

## 👤 Author

**Manimegalai V**

## 📞 Support

For issues or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include relevant screenshots or error logs

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLite Tutorial](https://www.sqlite.org/cli.html)

---

**Last Updated**: February 2026
