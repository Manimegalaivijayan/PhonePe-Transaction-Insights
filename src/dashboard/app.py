"""
PhonePe Pulse Analytics Dashboard
A comprehensive analytics platform for PhonePe transaction data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import custom modules
from analysis import query_executor_simple as qe
from dashboard.map_utils import (
    create_india_choropleth,
    normalize_state_name,
    format_large_number,
    get_district_data,
    create_district_bar_chart
)
from dashboard.business_cases import get_all_cases, get_selected_cases

# Page Configuration
st.set_page_config(
    page_title="PhonePe Pulse Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def _apply_hover_precision(fig):
    """Apply consistent 2-decimal hover formatting across Plotly charts."""
    if fig is None or not hasattr(fig, 'data'):
        return fig

    def is_year_like(values):
        if values is None:
            return False
        try:
            series = pd.Series(values).dropna()
            if series.empty:
                return False

            numeric = pd.to_numeric(series, errors='coerce').dropna()
            if numeric.empty or len(numeric) != len(series):
                return False

            numeric_values = [float(value) for value in numeric.tolist()]
            is_integer_like = all(abs(value - round(value)) < 1e-9 for value in numeric_values)
            is_year_range = all(1900 <= value <= 2100 for value in numeric_values)
            return bool(is_integer_like and is_year_range)
        except Exception:
            return False

    axis_updates = {}

    def get_layout_axis_key(axis_ref, axis_prefix):
        if axis_ref in (None, axis_prefix):
            return f"{axis_prefix}axis"
        return f"{axis_prefix}axis{axis_ref.replace(axis_prefix, '')}"

    for trace in fig.data:
        x_values = getattr(trace, 'x', None)
        y_values = getattr(trace, 'y', None)

        if is_year_like(x_values):
            x_ref = getattr(trace, 'xaxis', 'x')
            x_key = get_layout_axis_key(x_ref, 'x')
            axis_updates[x_key] = {
                'type': 'linear',
                'tickmode': 'linear',
                'dtick': 1,
                'tickformat': 'd',
                'hoverformat': 'd'
            }

        if is_year_like(y_values):
            y_ref = getattr(trace, 'yaxis', 'y')
            y_key = get_layout_axis_key(y_ref, 'y')
            axis_updates[y_key] = {
                'type': 'linear',
                'tickmode': 'linear',
                'dtick': 1,
                'tickformat': 'd',
                'hoverformat': 'd'
            }

    if axis_updates:
        try:
            fig.update_layout(**axis_updates)
        except Exception:
            pass

    try:
        fig.update_layout(
            xaxis_hoverformat='.2f',
            yaxis_hoverformat='.2f',
            yaxis2_hoverformat='.2f'
        )
    except Exception:
        pass

    for trace in fig.data:
        trace_type = getattr(trace, 'type', '')
        existing_hovertemplate = getattr(trace, 'hovertemplate', None)

        if existing_hovertemplate not in (None, ''):
            continue

        if trace_type in {'bar', 'scatter', 'scattergl', 'histogram', 'box', 'violin'}:
            trace.hovertemplate = "%{x}<br>%{y:.2f}<extra>%{fullData.name}</extra>"
        elif trace_type in {'pie', 'sunburst', 'treemap', 'funnelarea'}:
            trace.hovertemplate = "%{label}<br>%{value:.2f}<br>%{percent}<extra></extra>"
        elif trace_type in {'choropleth', 'choroplethmapbox'}:
            trace.hovertemplate = "%{location}<br>%{z:.2f}<extra></extra>"
        elif trace_type == 'heatmap':
            trace.hovertemplate = "x=%{x}<br>y=%{y}<br>value=%{z:.2f}<extra></extra>"

    if axis_updates:
        try:
            fig.update_layout(**axis_updates)
        except Exception:
            pass

    return fig


def _safe_numeric_round(values, digits=2):
    """Safely round numeric-like pandas values, coercing object dtypes to numeric."""
    numeric_values = pd.to_numeric(values, errors='coerce')
    return numeric_values.round(digits)


def _standardize_axis_title(title_text):
    """Standardize axis titles across charts for consistent naming."""
    if title_text is None:
        return None

    normalized = ' '.join(str(title_text).replace('_', ' ').strip().lower().split())
    if not normalized:
        return title_text

    title_map = {
        'year': 'Year',
        'quarter': 'Quarter',
        'users': 'Registered Users',
        'total users': 'Registered Users',
        'registered users': 'Registered Users',
        'transactions': 'Transactions',
        'total transactions': 'Transactions',
        'avg transactions': 'Average Transactions',
        'growth (%)': 'Growth Rate (%)',
        'growth rate (%)': 'Growth Rate (%)',
        'qoq growth (%)': 'Growth Rate (%)',
        'avg growth (%)': 'Average Growth Rate (%)',
        'market share (%)': 'Market Share (%)',
        'avg amount': 'Average Amount (₹)',
        'avg amount (₹)': 'Average Amount (₹)',
        'amount (billions ₹)': 'Amount (₹ Billions)',
        'trans/user': 'Transactions per User',
        'cumulative share (%)': 'Cumulative Share (%)',
        'individual share (%)': 'Individual Share (%)'
    }

    return title_map.get(normalized, title_text)


def _standardize_chart_title(title_text):
    """Standardize chart titles across the dashboard for consistent phrasing."""
    if title_text is None:
        return None

    normalized = ' '.join(str(title_text).replace('_', ' ').strip().lower().split())
    if not normalized:
        return title_text

    if normalized.startswith('top 5 device brands across top 10 states'):
        return 'Top 5 Device Brands Across Top 10 States'
    if normalized.startswith('device preference by region (top 5 brands across top 10 states)'):
        return 'Device Preference by Region (Top 5 Brands Across Top 10 States)'
    if normalized.startswith('top 10 states by total users'):
        return 'Top 10 States by Registered Users'
    if normalized.startswith('brand diversity vs user base'):
        return 'Brand Diversity vs Registered User Base'
    if normalized.startswith('top 15 states by transaction volume'):
        return 'Top 15 States by Transaction Volume'
    if normalized.startswith('top 15 states by transaction amount'):
        return 'Top 15 States by Transaction Amount (₹ Billions)'
    if normalized.startswith('top 10 states by transaction volume'):
        return 'Top 10 States by Transaction Volume'
    if normalized.startswith('quarter-over-quarter growth rate'):
        return 'Quarter-over-Quarter Growth Rate (%)'
    if normalized.startswith('yoy growth rate by transaction type'):
        return str(title_text).replace('YoY', 'Year-over-Year')

    return title_text


def _standardize_legend_title(title_text):
    """Standardize legend titles across charts."""
    if title_text is None:
        return None

    normalized = ' '.join(str(title_text).replace('_', ' ').strip().lower().split())
    if not normalized:
        return title_text

    title_map = {
        'brand': 'Brand',
        'transaction type': 'Transaction Type',
        'transaction_type': 'Transaction Type',
        'trend': 'Trend',
        'metric': 'Metric',
        'type': 'Type',
        'state': 'State'
    }
    return title_map.get(normalized, title_text)


def _normalize_state_like_text(label_text):
    """Normalize raw state-like labels (e.g., jammu-&-kashmir) for display."""
    if label_text is None:
        return label_text

    text = str(label_text)
    state_year_match = re.match(r'^(.*)\s\((\d{4})\)$', text)
    if state_year_match:
        state_part = state_year_match.group(1)
        year_part = state_year_match.group(2)
        normalized_state = normalize_state_name(state_part)
        return f"{normalized_state} ({year_part})"

    looks_state_like = ('-' in text) or ('&' in text) or text.islower()
    if looks_state_like:
        return normalize_state_name(text)

    return label_text


_streamlit_plotly_chart = st.plotly_chart


def plotly_chart_with_precision(fig, *args, **kwargs):
    """Wrapper to enforce 2-decimal precision in hover values for all charts."""
    fig = _apply_hover_precision(fig)

    axis_layout_updates = {}
    for axis_name in ['xaxis', 'xaxis2', 'yaxis', 'yaxis2']:
        axis_obj = getattr(fig.layout, axis_name, None)
        if axis_obj and getattr(axis_obj, 'title', None):
            current_title = axis_obj.title.text
            standardized_title = _standardize_axis_title(current_title)
            if standardized_title != current_title:
                axis_layout_updates[axis_name] = {'title': standardized_title}

    if axis_layout_updates:
        fig.update_layout(**axis_layout_updates)

    if getattr(fig.layout, 'title', None):
        current_title = fig.layout.title.text
        standardized_title = _standardize_chart_title(current_title)
        if standardized_title != current_title:
            fig.update_layout(title=standardized_title)

    if getattr(fig.layout, 'legend', None) and getattr(fig.layout.legend, 'title', None):
        current_legend_title = fig.layout.legend.title.text
        standardized_legend_title = _standardize_legend_title(current_legend_title)
        if standardized_legend_title != current_legend_title:
            fig.update_layout(legend_title_text=standardized_legend_title)

    for trace in fig.data:
        if getattr(trace, 'name', None):
            normalized_name = _normalize_state_like_text(trace.name)
            if normalized_name != trace.name:
                trace.name = normalized_name

        if hasattr(trace, 'x') and trace.x is not None:
            x_values = list(trace.x)
            normalized_x = [_normalize_state_like_text(value) for value in x_values]
            if normalized_x != x_values:
                trace.x = normalized_x

        if hasattr(trace, 'y') and trace.y is not None:
            y_values = list(trace.y)
            normalized_y = [_normalize_state_like_text(value) for value in y_values]
            if normalized_y != y_values:
                trace.y = normalized_y

    return _streamlit_plotly_chart(fig, *args, **kwargs)


st.plotly_chart = plotly_chart_with_precision

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    body {
        background: #f5f5f5 !important;
    }
    
    .stApp {
        background: #f5f5f5 !important;
    }
    
    .main {
        background: #f5f5f5 !important;
    }
    
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #000000 !important;
    }
    
    .main p, .main span, .main div, .main label {
        color: #000000 !important;
    }
    
    /* Ensure main content headers are always visible */
    .stApp h1, .stApp h2, .stApp h3 {
        color: #000000 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #2d3748;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Sidebar Selectbox styling */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
        background-color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] input,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] div[role="button"],
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] div {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {
        color: #000000 !important;
    }
    
    /* Sidebar dropdown menu options */
    [data-testid="stSidebar"] [data-baseweb="popover"] {
        background-color: #f0f4ff !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="menu"] {
        background-color: #f0f4ff !important;
    }
    
    [data-testid="stSidebar"] [role="option"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [role="option"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [role="option"] span {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [role="option"]:hover span {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [aria-selected="true"][role="option"] {
        background-color: #667eea !important;
        color: white !important;
    }
    
    [data-testid="stSidebar"] [aria-selected="true"][role="option"] span {
        color: white !important;
    }
    
    /* Override any highlighted state */
    [data-testid="stSidebar"] [role="option"][data-highlighted="true"] {
        background-color: #f0f2f6 !important;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [role="option"][data-highlighted="true"] span {
        color: #000000 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #718096;
        font-weight: 500;
    }
    
    [data-testid="stMetric"] {
        background: #f0f4ff;
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 1.5rem;
        padding-top: 2rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
    }
    
    /* Charts - Dark Theme */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background: #1a1a1a !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander */
    div[data-testid="stExpander"] details {
        margin-bottom: 1.5rem !important;
    }
    
    div[data-testid="stExpander"] summary {
        background: #f0f4ff !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #2d3748 !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) !important;
    }
    
    div[data-testid="stExpander"] summary:hover {
        background: #f7fafc !important;
        border-color: #764ba2 !important;
    }
    
    div[data-testid="stExpander"] .streamlit-expanderContent {
        border: 2px solid #667eea !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
        background: #f0f4ff !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* Radio */
    .stRadio > div {
        color: #000000 !important;
    }
    
    .stRadio label {
        color: #000000 !important;
    }
    
    .stRadio div[role="radiogroup"] label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    .stRadio > label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stRadio [role="radiogroup"] label span {
        color: #000000 !important;
    }
    
    /* Radio button options and circles */
    .stRadio div[role="radiogroup"] {
        color: #000000 !important;
    }
    
    .stRadio div[role="radiogroup"] > div {
        color: #000000 !important;
    }
    
    .stRadio div[role="radiogroup"] > label > span {
        color: #000000 !important;
    }
    
    .stRadio [data-baseweb="radio"] {
        color: #000000 !important;
    }
    
    [data-baseweb="radio"] svg {
        color: #000000 !important;
        fill: #000000 !important;
    }
    
    /* Selectbox - White background with black text */
    .stSelectbox label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox > label > span {
        color: #000000 !important;
    }
    
    /* Dropdown/Popover styling */
    [data-baseweb="popover"] {
        background-color: #f0f4ff !important;
    }
    
    [data-baseweb="menu"] {
        background-color: #f0f4ff !important;
    }
    
    [data-baseweb="menu"] > div {
        background-color: #f0f4ff !important;
    }
    
    [data-baseweb="menu"] [role="option"] {
        color: #000000 !important;
        background-color: #f0f4ff !important;
    }
    
    [data-baseweb="menu"] [role="option"] span {
        color: #000000 !important;
    }
    
    [data-baseweb="menu"] [role="option"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Universal text color fix for ALL areas (sidebar + main) */
    .stRadio, .stSelectbox {
        color: #000000 !important;
    }
    
    .stRadio *, .stSelectbox * {
        color: #000000 !important;
    }
    
    .stRadio span, .stSelectbox span {
        color: #000000 !important;
    }
    
    .stRadio div, .stSelectbox div {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Additional label styling for visibility */
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] span[class*="stLabel"] {
        color: #000000 !important;
    }
    
    .stRadio > label,
    .stSelectbox > label,
    [data-testid="stSidebar"] div span {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label > span,
    [data-testid="stSidebar"] .stSelectbox > label > span,
    [data-testid="stSidebar"] .stRadio span,
    [data-testid="stSidebar"] .stSelectbox span {
        color: #000000 !important;
    }
    
    /* Universal label text color fix */
    label {
        color: #000000 !important;
    }
    
    label span {
        color: #000000 !important;
    }
    
    .streamlit-expanderContent label,
    .streamlit-expanderContent label span {
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        border: 1px solid #4a5568 !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white !important;
    }
    
    .stSelectbox [data-baseweb="select"] input {
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] div[role="button"] {
        color: #000000 !important;
    }
    
    .stSelectbox [data-baseweb="select"] svg {
        color: #000000 !important;
    }
    
    [data-baseweb="popover"] {
        background-color: white !important;
    }
    
    [data-baseweb="menu"] {
        background-color: white !important;
    }
    
    [role="option"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="option"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    [role="option"] span {
        color: #000000 !important;
    }
    
    [role="option"]:hover span {
        color: #000000 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f0f4ff;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        color: #4a5568;
        font-weight: 500;
        border: 1px solid #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    /* Heading visibility - ensure all headings are black and visible */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }
    
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Tab content headings */
    .stTabs [role="tab"] {
        color: #000000 !important;
    }
    
    .stTabs h2, .stTabs h3, .stTabs h4 {
        color: #000000 !important;
    }
    
    /* Expander content */
    [data-testid="stExpander"] h2,
    [data-testid="stExpander"] h3,
    [data-testid="stExpander"] h4 {
        color: #000000 !important;
    }
    
    /* All markdown text */
    [data-testid="stMarkdownContainer"] {
        color: #000000 !important;
    }
    
    [data-testid="stMarkdownContainer"] * {
        color: #000000 !important;
    }
    
    /* Header menu (three dots) styling */
    [data-testid="stTopBar"] {
        background: white !important;
    }
    
    .st-emotion-cache-1y0h4nx {
        background-color: white !important;
    }
    
    /* Main menu button and options */
    [role="menu"] {
        background-color: #f0f4ff !important;
        border-radius: 8px !important;
        border: 2px solid #667eea !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    [role="menuitem"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    [role="menuitem"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    [role="menuitem"] span {
        color: #000000 !important;
    }
    
    /* Ensure all menu items have light background */
    [role="menu"] [role="menuitem"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="menu"] [role="menuitem"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Streamlit menu popover override */
    [data-testid="stBaseButton-secondary"] {
        color: #000000 !important;
    }
    
    /* All div and button elements in menus */
    [role="menu"] div {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="menu"] button {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="menu"] button:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Fallback for all menu-like elements */
    .st-emotion-cache * [role="menuitem"],
    [data-baseweb="menu"] [role="menuitem"],
    div[role="menu"] > div,
    div[role="menu"] > button {
        background-color: #f0f4ff !important;
        color: #000000 !important;
        border-color: #667eea !important;
    }
    
    div[role="menu"] > div:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Target Streamlit-specific menu styling */
    .st-emotion-cache-1gv5ylf {
        background-color: #f0f4ff !important;
    }
    
    .st-emotion-cache-1r4qwoa {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    /* All children of menu */
    [role="menu"] > * {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="menu"] > *:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Override dark backgrounds in menus */
    div[data-testid*="menu"],
    div[role="menu"] {
        background-color: #f0f4ff !important;
    }
    
    div[data-testid*="menu"] *,
    div[role="menu"] * {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    div[role="menu"] > div > * {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    /* Nested menu items */
    [role="menu"] [role="option"],
    [role="menu"] [role="button"],
    [role="menu"] [role="link"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="menu"] [role="option"]:hover,
    [role="menu"] [role="button"]:hover,
    [role="menu"] [role="link"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Target Streamlit header menu - the three dots menu */
    [data-testid="stToolbar"] [data-baseweb="popover"] {
        background-color: #f0f4ff !important;
    }
    
    [data-testid="stToolbar"] [data-baseweb="menu"] {
        background-color: #f0f4ff !important;
    }
    
    [data-testid="stToolbar"] [role="menuitem"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [data-testid="stToolbar"] [role="menuitem"]:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    [data-testid="stToolbar"] [role="menuitem"] span {
        color: #000000 !important;
    }
    
    /* Additional menu styling for header */
    [data-testid="stElementContainer"] [data-baseweb="popover"],
    [data-testid="stElementContainer"] [data-baseweb="menu"] {
        background-color: #f0f4ff !important;
    }
    
    /* Ensure popover children are light */
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"] > div {
        background-color: #f0f4ff !important;
    }
    
    [data-baseweb="popover"] > div > *,
    [data-baseweb="menu"] > div > * {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    /* AGGRESSIVE: Override ALL dark backgrounds in any popup/menu */
    [data-testid*="popover"],
    [data-testid*="menu"],
    [role="menu"],
    [role="listbox"],
    [role="dialog"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [data-testid*="popover"] *,
    [data-testid*="menu"] *,
    [role="menu"] *,
    [role="listbox"] *,
    [role="dialog"] * {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    /* Target all children recursively */
    [role="menu"] div,
    [role="menu"] button,
    [role="menu"] span,
    [role="menu"] p {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    [role="menu"] div:hover,
    [role="menu"] button:hover {
        background-color: #e6ecff !important;
        color: #000000 !important;
    }
    
    /* Streamlit popover specific */
    .st-emotion-cache-iiif86 {
        background-color: #f0f4ff !important;
    }
    
    .st-emotion-cache-iiif86 * {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
    
    /* Last resort - override any dark color styles */
    *[style*="background-color: rgb(45, 55, 72)"],
    *[style*="background-color: #2d3748"],
    *[style*="background: rgb(45, 55, 72)"],
    *[style*="background: #2d3748"] {
        background-color: #f0f4ff !important;
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Database Connection
@st.cache_resource
def get_db_connection():
    """Initialize database connection"""
    base_dir = Path(__file__).parent.parent.parent
    db_path = base_dir / "data" / "phonepe_pulse.db"
    return qe.connect_database(str(db_path))

# Main Application
def main():
    conn = get_db_connection()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0;">
            <h1 style="font-size: 1.75rem; margin: 0; color: white;">📊 PhonePe Pulse</h1>
            <p style="font-size: 0.875rem; opacity: 0.8; margin-top: 0.5rem; color: white;">Analytics Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page",
            ["🏠 Home", "📈 Business Cases"],
            label_visibility="collapsed"
        )
        
        # Business Case Selection (moved here, right after navigation)
        if page == "📈 Business Cases":
            st.markdown("---")
            st.markdown("### Business Case")
            
            all_cases = get_all_cases()
            case_titles = [f"{case['title']}" for case in all_cases.values()]
            case_ids = list(all_cases.keys())
            
            selected_case_idx = st.selectbox(
                "Select Case",
                range(len(case_titles)),
                format_func=lambda x: case_titles[x],
                label_visibility="collapsed"
            )
            
            selected_case_id = case_ids[selected_case_idx]
        else:
            selected_case_id = None
        
        st.markdown("---")
        
        # Filters
        st.markdown("### Filters")

        years_query = """
        SELECT DISTINCT year
        FROM aggregated_transaction
        ORDER BY year DESC
        """
        years_df = qe.execute_query(conn, years_query)
        year_options = ["All"] + [str(int(year)) for year in years_df['year'].dropna().tolist()]
        
        year_filter = st.selectbox(
            "Year",
            year_options,
            index=0
        )
        
        quarter_filter = st.selectbox(
            "Quarter",
            ["All", "1", "2", "3", "4"],
            index=0
        )
        
        # Get states for filter
        states_query = """
        SELECT DISTINCT state FROM aggregated_transaction 
        WHERE state != 'All India' 
        ORDER BY state
        """
        states_df = qe.execute_query(conn, states_query)
        state_options = ["All India"] + states_df['state'].tolist()
        
        state_filter = st.selectbox(
            "State",
            state_options,
            index=0
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: white;">
            <p style="font-size: 0.75rem; opacity: 0.7; margin: 0;">Built with Streamlit & Plotly</p>
            <p style="font-size: 0.75rem; opacity: 0.7; margin: 0;">Data: PhonePe Pulse</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: white;">
            <p style="font-size: 0.7rem; opacity: 0.5; margin: 0 0 0.5rem 0;">Created by</p>
            <p style="font-size: 0.9rem; font-weight: 600; margin: 0; color: #a78bfa;">Manimegalai V</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content
    if page == "🏠 Home":
        show_home_page(conn, year_filter, quarter_filter, state_filter)
    elif page == "📈 Business Cases" and selected_case_id:
        case_data = get_all_cases()[selected_case_id]
        show_business_case(selected_case_id, case_data, conn, year_filter, quarter_filter, state_filter)

def show_home_page(conn, year_filter, quarter_filter, state_filter):
    """Display the home page"""
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
        <div style="font-size: 3.5rem; margin-bottom: 1rem;">📊</div>
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #000000; margin: 0;">
            PhonePe Pulse Analytics
        </h1>
        <p style="font-size: 1.1rem; color: #000000; margin-top: 0.5rem;">
            Data-Driven Insights for Digital Payment Excellence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome Message
    st.markdown("""
    <div style="background: white; border-left: 4px solid #667eea; padding: 1.5rem; border-radius: 8px; margin-bottom: 3rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="font-size: 1.05rem; line-height: 1.7; color: #000000; margin: 0;">
            Explore comprehensive insights into PhonePe's digital payment ecosystem. Analyze <strong>transactions</strong>, 
            <strong>user engagement</strong>, and <strong>insurance services</strong> across India with interactive visualizations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown("""
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #000000; margin: 2rem 0 1.5rem 0;">
        📊 Key Performance Indicators
    </h2>
    """, unsafe_allow_html=True)
    
    # Get metrics with filters
    state_condition = f"AND state = '{state_filter}'" if state_filter != "All India" else "AND state = 'All India'"
    state_scope_condition = f"AND state = '{state_filter}'" if state_filter != "All India" else "AND state != 'All India'"
    year_condition = f"AND year = {year_filter}" if year_filter != "All" else ""
    quarter_condition = f"AND quarter = {quarter_filter}" if quarter_filter != "All" else ""
    
    metrics_query = f"""
    SELECT 
        SUM(transaction_count) as total_transactions,
        ROUND(SUM(transaction_amount) / 1e12, 2) as total_amount_trillions
    FROM aggregated_transaction
    WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
    """
    
    users_query = f"""
    SELECT SUM(registered_users) as total_users
    FROM aggregated_user
    WHERE brand = 'Total' {state_condition} {year_condition} {quarter_condition}
    """
    
    growth_query = f"""
    SELECT 
        year,
        SUM(transaction_count) as yearly_trans
    FROM aggregated_transaction
    WHERE 1=1 {state_condition}
    GROUP BY year
    ORDER BY year DESC
    LIMIT 2
    """
    
    metrics_df = qe.execute_query(conn, metrics_query)
    users_df = qe.execute_query(conn, users_query)
    growth_df = qe.execute_query(conn, growth_query)
    
    # Calculate growth
    if len(growth_df) >= 2:
        latest = growth_df.iloc[0]['yearly_trans']
        previous = growth_df.iloc[1]['yearly_trans']
        growth_pct = round((latest - previous) * 100.0 / previous, 2)
    else:
        growth_pct = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔢 Total Transactions",
            value=f"{metrics_df.iloc[0]['total_transactions'] / 1e9:.2f}B",
            delta=f"+{growth_pct}% YoY"
        )
    
    with col2:
        st.metric(
            label="💰 Total Amount",
            value=f"₹{metrics_df.iloc[0]['total_amount_trillions']:.2f}T",
            delta="Growing"
        )
    
    with col3:
        st.metric(
            label="👥 Registered Users",
            value=f"{users_df.iloc[0]['total_users'] / 1e9:.2f}B",
            delta="Active"
        )
    
    with col4:
        st.metric(
            label="🗺️ States Covered",
            value="36",
            delta="All India"
        )
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Transaction Trends
    st.markdown("""
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem;">
        📈 Transaction Trends Over Time
    </h2>
    """, unsafe_allow_html=True)
    
    trends_query = f"""
    SELECT 
        year,
        SUM(transaction_count) as total_transactions,
        ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
    FROM aggregated_transaction
    WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
    GROUP BY year
    ORDER BY year
    """
    
    trends_df = qe.execute_query(conn, trends_query)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            trends_df, 
            x='year', 
            y='total_transactions',
            title='Total Transactions by Year',
            markers=True
        )
        fig.update_traces(
            line_color='#a78bfa',
            line_width=3,
            marker=dict(size=10, color='#a78bfa')
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=16, color='white'),
            xaxis=dict(showgrid=False, color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            hovermode='x unified',
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            trends_df,
            x='year',
            y='amount_billions',
            title='Transaction Amount by Year (Billions ₹)'
        )
        fig.update_traces(marker_color='#a78bfa')
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=16, color='white'),
            xaxis=dict(showgrid=False, color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Geographic Analysis
    st.markdown("""
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem;">
        🗺️ Interactive Geographic Analysis
    </h2>
    """, unsafe_allow_html=True)
    
    col_map, col_controls = st.columns([3, 1])
    
    with col_controls:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="color: #000000; margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600;">Map Controls</h4>
        """, unsafe_allow_html=True)
        
        map_metric = st.radio(
            "Select Metric",
            ["Transactions", "Amount"],
            key="home_map_metric"
        )
        
        map_year = st.selectbox(
            "Select Year",
            ["2024", "2023", "2022", "All"],
            key="home_map_year"
        )
        
        st.markdown("""
        </div>
        <div style="background: #f7fafc; border: 1px solid #cbd5e0; border-left: 3px solid #667eea; padding: 1rem; border-radius: 4px; margin-top: 1rem;">
            <p style="font-size: 0.875rem; line-height: 1.6; color: #000000; margin: 0;">
                💡 <strong>Tip:</strong> Hover over states for details
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_map:
        year_cond = f"AND year = {map_year}" if map_year != "All" else "AND year >= 2022"
        map_query = f"""
        SELECT 
            state,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE state != 'All India' {year_cond}
        GROUP BY state
        """
        map_df = qe.execute_query(conn, map_query)
        
        if map_metric == "Transactions":
            map_fig = create_india_choropleth(
                map_df,
                'total_transactions',
                f'Transaction Volume Across India ({map_year})',
                color_scale='Purples'
            )
        else:
            map_fig = create_india_choropleth(
                map_df,
                'amount_billions',
                f'Transaction Amount Across India ({map_year})',
                color_scale='Blues'
            )
        
        st.plotly_chart(map_fig, use_container_width=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Top States
    st.markdown("""
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 1.5rem;">
        🏆 Top 15 States Analysis
    </h2>
    """, unsafe_allow_html=True)
    
    top_states_query = f"""
    SELECT 
        state,
        SUM(transaction_count) as total_transactions,
        ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
    FROM aggregated_transaction
    WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
    GROUP BY state
    ORDER BY total_transactions DESC
    LIMIT 15
    """
    
    top_states_df = qe.execute_query(conn, top_states_query)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            top_states_df,
            x='state',
            y='total_transactions',
            title='Top 15 States by Transaction Volume',
            color='total_transactions',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=16, color='white'),
            xaxis=dict(tickangle=45, showgrid=False, color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            showlegend=False,
            margin=dict(l=40, r=20, t=50, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            top_states_df,
            x='state',
            y='amount_billions',
            title='Top 15 States by Transaction Amount (Billions ₹)',
            color='amount_billions',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=16, color='white'),
            xaxis=dict(tickangle=45, showgrid=False, color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            showlegend=False,
            margin=dict(l=40, r=20, t=50, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Business Value Propositions with Metrics
    st.markdown("""
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 0.5rem;">
        💼 Business Value & Use Cases
    </h2>
    <p style="font-size: 1rem; color: #000000; margin-bottom: 1.5rem;">
        Discover how PhonePe Pulse data drives strategic decisions across multiple business domains
    </p>
    """, unsafe_allow_html=True)
    
    # Fetch metrics for business values with filters
    bv_metrics_query = f"""
    SELECT 
        COUNT(DISTINCT state) as total_states,
        SUM(transaction_count) as total_trans,
        COUNT(DISTINCT transaction_type) as trans_types
    FROM aggregated_transaction
    WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
    """
    
    bv_districts_query = f"""
    SELECT COUNT(DISTINCT district) as total_districts
    FROM map_transaction
    WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
    """
    
    bv_user_query = f"""
    SELECT SUM(registered_users) as total_users
    FROM aggregated_user
    WHERE brand = 'Total' {state_condition} {year_condition} {quarter_condition}
    """
    
    bv_growth_query = f"""
    SELECT 
        year,
        SUM(transaction_count) as yearly_trans
    FROM aggregated_transaction
    WHERE 1=1 {state_condition}
    GROUP BY year
    ORDER BY year DESC
    LIMIT 2
    """
    
    bv_metrics = qe.execute_query(conn, bv_metrics_query).iloc[0]
    bv_districts = qe.execute_query(conn, bv_districts_query).iloc[0]
    bv_users = qe.execute_query(conn, bv_user_query).iloc[0]
    bv_growth = qe.execute_query(conn, bv_growth_query)
    
    if len(bv_growth) >= 2:
        yoy_growth = round((bv_growth.iloc[0]['yearly_trans'] - bv_growth.iloc[1]['yearly_trans']) * 100.0 / bv_growth.iloc[1]['yearly_trans'], 2)
    else:
        yoy_growth = 0
    
    # Business values with relevant metrics and details
    business_values = [
        {
            "icon": "🎯",
            "title": "Customer Segmentation",
            "description": "Identify distinct user groups based on spending habits to tailor marketing strategies.",
            "metric": f"{bv_users['total_users']/1e9:.2f}B Users",
            "details": [
                "Segment users by transaction frequency and value",
                "Target high-value customers with personalized offers",
                "Optimize customer acquisition strategies"
            ]
        },
        {
            "icon": "🛡️",
            "title": "Fraud Detection",
            "description": "Analyze transaction patterns to spot and prevent fraudulent activities.",
            "metric": f"{bv_metrics['total_trans']/1e9:.2f}B Transactions",
            "details": [
                "Monitor anomalous transaction patterns in real-time",
                "Identify suspicious behavioral changes",
                "Reduce fraud losses and improve security"
            ]
        },
        {
            "icon": "🗺️",
            "title": "Geographical Insights",
            "description": "Understand payment trends at state and district levels for targeted marketing.",
            "metric": f"{int(bv_metrics['total_states'])} States",
            "details": [
                "Identify high-growth regions for expansion",
                "Localize marketing campaigns by region",
                "Optimize resource allocation geographically"
            ]
        },
        {
            "icon": "💳",
            "title": "Payment Performance",
            "description": "Evaluate the popularity of different payment categories for strategic investments.",
            "metric": f"{int(bv_metrics['trans_types'])} Categories",
            "details": [
                "Track category-wise transaction trends",
                "Optimize payment method offerings",
                "Invest in high-performing categories"
            ]
        },
        {
            "icon": "📱",
            "title": "User Engagement",
            "description": "Monitor user activity to develop strategies that enhance retention and satisfaction.",
            "metric": f"+{yoy_growth}% Growth",
            "details": [
                "Measure daily active users and retention rates",
                "Identify drivers of user engagement",
                "Develop strategies to boost repeat usage"
            ]
        },
        {
            "icon": "🚀",
            "title": "Product Development",
            "description": "Use data insights to inform the creation of new features and services.",
            "metric": "Data-Driven",
            "details": [
                "Identify feature gaps through usage patterns",
                "Prioritize product roadmap based on data",
                "Validate new features with A/B testing"
            ]
        },
        {
            "icon": "🏥",
            "title": "Insurance Insights",
            "description": "Analyze insurance transaction data to improve product offerings and customer experience.",
            "metric": "Multi-Sector",
            "details": [
                "Track insurance product adoption rates",
                "Identify cross-selling opportunities",
                "Optimize insurance product portfolio"
            ]
        },
        {
            "icon": "📢",
            "title": "Marketing Optimization",
            "description": "Tailor marketing campaigns based on user behavior and transaction patterns.",
            "metric": f"{int(bv_districts['total_districts'])}+ Districts",
            "details": [
                "Measure campaign ROI and effectiveness",
                "Target campaigns to specific user segments",
                "Optimize marketing spend allocation"
            ]
        },
        {
            "icon": "📈",
            "title": "Trend Analysis",
            "description": "Examine transaction trends over time to anticipate demand fluctuations.",
            "metric": "YoY Tracking",
            "details": [
                "Forecast future transaction volumes",
                "Identify seasonal patterns and trends",
                "Plan capacity and resources proactively"
            ]
        },
        {
            "icon": "🏆",
            "title": "Competitive Benchmarking",
            "description": "Compare performance against competitors to identify areas for improvement.",
            "metric": "360° View",
            "details": [
                "Benchmark against industry standards",
                "Identify competitive advantages",
                "Track market share and positioning"
            ]
        }
    ]
    
    
    # Display in expandable cards
    for idx, value in enumerate(business_values):
        with st.expander(f"{value['icon']} **{value['title']}** - {value['metric']}", expanded=False):
            st.markdown(f"""
            <div style="padding: 0.5rem 0;">
                <p style="color: #4a5568; font-size: 1rem; margin-bottom: 1rem; line-height: 1.7;">
                    {value['description']}
                </p>
                <h4 style="color: #2d3748; font-size: 0.95rem; font-weight: 600; margin: 1rem 0 0.5rem 0;">
                    💡 Key Applications:
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            for detail in value['details']:
                st.markdown(f"""
                <div style="background: #f7fafc; border-left: 3px solid #667eea; padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 4px;">
                    <span style="color: #2d3748; font-size: 0.9rem;">✓ {detail}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Business Cases Preview
    st.markdown("""
    <h2 style="font-size: 1.5rem; font-weight: 700; color: #000000; margin-bottom: 0.5rem;">
        📋 Business Case Studies
    </h2>
    <p style="font-size: 1rem; color: #000000; margin-bottom: 1.5rem;">
        Select a business case from the sidebar to explore detailed analysis
    </p>
    """, unsafe_allow_html=True)
    
    all_cases = get_all_cases()
    
    for case_id, case in all_cases.items():
        with st.expander(f"**{case['title']}**", expanded=False):
            st.write(case['description'])
            st.markdown("**Key Questions:**")
            for question in case['key_questions']:
                st.markdown(f"- {question}")

def show_business_case(case_id, case_data, conn, year_filter, quarter_filter, state_filter):
    """Display business case analysis"""
    
    # Header
    st.markdown(f"""
    <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #000000; margin: 0;">
            {case_data['title']}
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Description
    st.markdown(f"""
    <div style="background: white; border-left: 4px solid #667eea; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="font-size: 1.05rem; line-height: 1.7; color: #000000; margin: 0;">
            {case_data["description"]}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Questions
    st.markdown("""
    <h3 style="font-size: 1.25rem; font-weight: 600; color: #000000; margin: 2rem 0 1rem 0;">
        🎯 Key Questions
    </h3>
    """, unsafe_allow_html=True)
    
    for i, question in enumerate(case_data['key_questions'], 1):
        st.markdown(f"""
        <div style="background: white; border-left: 3px solid #667eea; padding: 1rem; margin-bottom: 0.75rem; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <span style="color: #000000; font-size: 0.95rem;">
                <strong style="color: #667eea;">{i}.</strong> {question}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📉 Trends", "🗺️ Geographic", "💡 Insights"])
    
    with tab1:
        show_overview_section(case_id, conn, year_filter, quarter_filter, state_filter)
    
    with tab2:
        show_trends_section(case_id, conn, year_filter, quarter_filter, state_filter)
    
    with tab3:
        show_geographical_section(case_id, conn, year_filter, quarter_filter, state_filter)
    
    with tab4:
        show_insights_section(case_id, case_data, conn)

def show_overview_section(case_id, conn, year_filter, quarter_filter, state_filter):
    """Display overview metrics"""
    st.markdown("""
    <h3 style="font-size: 1.125rem; font-weight: 600; color: #000000; margin: 1rem 0;">
        Key Metrics Overview
    </h3>
    """, unsafe_allow_html=True)
    
    year_condition = f"AND year = {year_filter}" if year_filter != "All" else ""
    quarter_condition = f"AND quarter = {quarter_filter}" if quarter_filter != "All" else ""
    state_condition = f"AND state = '{state_filter}'" if state_filter != "All India" else "AND state = 'All India'"
    
    if case_id == "case_1":
        query = f"""
        SELECT 
            COUNT(DISTINCT transaction_type) as payment_types,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
        """
        df = qe.execute_query(conn, query)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            payment_types = df.iloc[0]['payment_types'] if df is not None and not df.empty else 0
            st.metric("💳 Payment Types", f"{payment_types}")
        with col2:
            total_trans = df.iloc[0]['total_transactions'] if df is not None and not df.empty and df.iloc[0]['total_transactions'] is not None else 0
            st.metric("🔢 Total Transactions", f"{total_trans / 1e9:.2f}B")
        with col3:
            amount = df.iloc[0]['amount_billions'] if df is not None and not df.empty and df.iloc[0]['amount_billions'] is not None else 0
            st.metric("💰 Total Amount", f"₹{amount:.2f}B")
        
        # Question 2: Which transaction types drive the highest value?
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                ❓ Question 2: Which transaction types drive the highest value?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        correlation_query = f"""
        SELECT 
            transaction_type,
            SUM(transaction_count) as total_count,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions,
            ROUND(SUM(transaction_amount) / SUM(transaction_count), 2) as avg_ticket_size
        FROM aggregated_transaction
        WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
        GROUP BY transaction_type
        ORDER BY total_count DESC
        """
        df_corr = qe.execute_query(conn, correlation_query)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if df_corr is not None and not df_corr.empty:
                # Ensure data types are numeric
                df_corr['total_count'] = pd.to_numeric(df_corr['total_count'], errors='coerce')
                df_corr['amount_billions'] = pd.to_numeric(df_corr['amount_billions'], errors='coerce')
                df_corr['avg_ticket_size'] = pd.to_numeric(df_corr['avg_ticket_size'], errors='coerce')
                df_corr = df_corr.dropna()
                
                if not df_corr.empty:
                    fig = px.scatter(
                        df_corr,
                        x='total_count',
                        y='amount_billions',
                        size='avg_ticket_size',
                        color='transaction_type',
                        title='Transaction Volume vs Amount by Type',
                        hover_data=['avg_ticket_size'],
                        labels={'total_count': 'Transaction Count', 'amount_billions': 'Amount (Billions ₹)'}
                    )
                    fig.update_layout(
                        plot_bgcolor='#1a1a1a',
                        paper_bgcolor='#1a1a1a',
                        font=dict(color='white', family='Poppins, sans-serif'),
                        title_font=dict(size=14, color='white'),
                        xaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                        yaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                        legend=dict(font=dict(color='white')),
                        margin=dict(l=40, r=20, t=50, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No correlation data available for scatter plot")
        
        with col2:
            if df_corr is not None and not df_corr.empty:
                df_sorted = df_corr.sort_values('avg_ticket_size', ascending=False)
                fig = px.bar(
                    df_sorted,
                    x='transaction_type',
                    y='avg_ticket_size',
                    title='Average Ticket Size by Transaction Type',
                    color='avg_ticket_size',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    font=dict(color='white', family='Poppins, sans-serif'),
                    title_font=dict(size=14, color='white'),
                    xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                    yaxis=dict(gridcolor='#333333', color='white', title='Avg Amount (₹)'),
                    showlegend=False,
                    margin=dict(l=40, r=20, t=50, b=100)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No bar chart data available")
        
    elif case_id == "case_2":
        query = f"""
        SELECT 
            COUNT(DISTINCT brand) as device_brands,
            SUM(registered_users) as total_users
        FROM aggregated_user
        WHERE brand != 'Total' {state_condition} {year_condition} {quarter_condition}
        """
        df = qe.execute_query(conn, query)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            device_brands = df.iloc[0]['device_brands'] if df is not None and not df.empty else 0
            st.metric("📱 Device Brands", f"{device_brands}")
        with col2:
            total_users = df.iloc[0]['total_users']
            if total_users is not None:
                st.metric("👥 Total Users", f"{total_users / 1e6:.2f}M")
            else:
                st.metric("👥 Total Users", "N/A")
        with col3:
            # Calculate top brand dominance
            top_brand_query = f"""
            SELECT MAX(pct) as top_share
            FROM (
                SELECT ROUND(SUM(registered_users) * 100.0 / (SELECT SUM(registered_users) FROM aggregated_user WHERE brand != 'Total' {state_condition} {year_condition} {quarter_condition}), 2) as pct
                FROM aggregated_user
                WHERE brand != 'Total' {state_condition} {year_condition} {quarter_condition}
                GROUP BY brand
            )
            """
            top_share_df = qe.execute_query(conn, top_brand_query)
            top_share = top_share_df.iloc[0]['top_share'] if top_share_df is not None and not top_share_df.empty and top_share_df.iloc[0]['top_share'] is not None else 0
            st.metric("🏆 Top Brand Share", f"{top_share:.2f}%")
        
        # Question 1 & 3: Which device brands dominate and user engagement patterns
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                ❓ Question 1 & 3: Which device brands dominate & user engagement patterns?
            </p>
        </div>
        """, unsafe_allow_html=True)

        min_users_threshold = 1000000 if state_filter == "All India" else 0
        
        engagement_query = f"""
        SELECT 
            u.brand,
            SUM(u.registered_users) as total_users
        FROM aggregated_user u
        WHERE u.brand != 'Total' {state_condition} {year_condition} {quarter_condition}
        GROUP BY u.brand
        HAVING SUM(u.registered_users) > {min_users_threshold}
        ORDER BY total_users DESC
        LIMIT 15
        """
        df_engagement = qe.execute_query(conn, engagement_query)
        
        fig = px.bar(
            df_engagement,
            x='brand',
            y='total_users',
            title='Total Registered Users by Top Brands',
            color='total_users',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=14, color='white'),
            xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
            yaxis=dict(gridcolor='#333333', color='white', title='Users'),
            showlegend=False,
            margin=dict(l=40, r=20, t=50, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        query = f"""
        SELECT 
            COUNT(DISTINCT state) as states_count,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
        """
        df = qe.execute_query(conn, query)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            states_count = df.iloc[0]['states_count'] if df is not None and not df.empty else 0
            st.metric("🗺️ States", f"{states_count}")
        with col2:
            total_transactions = df.iloc[0]['total_transactions'] if df is not None and not df.empty and df.iloc[0]['total_transactions'] is not None else 0
            st.metric("🔢 Transactions", f"{total_transactions / 1e9:.2f}B")
        with col3:
            amount_billions = df.iloc[0]['amount_billions'] if df is not None and not df.empty and df.iloc[0]['amount_billions'] is not None else 0
            st.metric("💰 Amount", f"₹{amount_billions:.2f}B")

def show_trends_section(case_id, conn, year_filter, quarter_filter, state_filter):
    """Display trend analysis"""
    st.markdown("#### 📈 Trend Analysis")
    
    year_condition = f"AND year = {year_filter}" if year_filter != "All" else ""
    quarter_condition = f"AND quarter = {quarter_filter}" if quarter_filter != "All" else ""
    state_condition = f"AND state = '{state_filter}'" if state_filter != "All India" else "AND state = 'All India'"
    state_scope_condition = f"AND state = '{state_filter}'" if state_filter != "All India" else "AND state != 'All India'"
    
    if case_id == "case_1":
        # Question 1: What are the year-over-year transaction growth rates?
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                ❓ Question 1: What are the year-over-year transaction growth rates?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        yoy_year_condition = ""
        selected_year = None
        if year_filter != "All":
            selected_year = int(year_filter)
            yoy_year_condition = f"AND year IN ({selected_year - 1}, {selected_year})"

        growth_query = f"""
        WITH yearly_data AS (
            SELECT 
                transaction_type,
                year,
                SUM(transaction_amount) as amount
            FROM aggregated_transaction
            WHERE 1=1 {state_condition} {yoy_year_condition} {quarter_condition}
            GROUP BY transaction_type, year
        )
        SELECT 
            transaction_type,
            year,
            amount,
            LAG(amount) OVER (PARTITION BY transaction_type ORDER BY year) as prev_year_amount
        FROM yearly_data
        ORDER BY transaction_type, year
        """
        
        df_growth = qe.execute_query(conn, growth_query)
        df_growth['growth_rate'] = _safe_numeric_round(
            (df_growth['amount'] - df_growth['prev_year_amount']) / df_growth['prev_year_amount'] * 100,
            2
        )
        df_growth_filtered = df_growth[df_growth['prev_year_amount'].notna()]

        if selected_year is not None:
            df_growth_filtered = df_growth_filtered[df_growth_filtered['year'] == selected_year]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Growth rate comparison
            if df_growth_filtered.empty:
                st.info("No YoY growth data available for the selected year and filters.")
            else:
                latest_year = df_growth_filtered['year'].max()
                df_latest = df_growth_filtered[df_growth_filtered['year'] == latest_year].sort_values('growth_rate', ascending=False)
            
                fig = px.bar(
                    df_latest,
                    x='transaction_type',
                    y='growth_rate',
                    title=f'YoY Growth Rate by Transaction Type ({latest_year})',
                    color='growth_rate',
                    color_continuous_scale=['#ef4444', '#fbbf24', '#10b981']
                )
                fig.update_layout(
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    font=dict(color='white', family='Poppins, sans-serif'),
                    title_font=dict(size=14, color='white'),
                    xaxis=dict(showgrid=False, color='white', title=''),
                    yaxis=dict(gridcolor='#333333', color='white', title='Growth Rate (%)'),
                    showlegend=False,
                    margin=dict(l=40, r=20, t=50, b=80)
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Question 3: Are there seasonal patterns in digital payments?
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                ❓ Question 3: Are there seasonal patterns in digital payments?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        seasonal_query = f"""
        SELECT 
            quarter,
            AVG(transaction_count) as avg_transactions,
            AVG(transaction_amount) as avg_amount
        FROM aggregated_transaction
        WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
        GROUP BY quarter
        ORDER BY quarter
        """
        df_seasonal = qe.execute_query(conn, seasonal_query)
        df_seasonal['quarter_label'] = 'Q' + df_seasonal['quarter'].astype(str)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df_seasonal,
                x='quarter_label',
                y='avg_transactions',
                title='Average Transactions by Quarter',
                text='avg_transactions'
            )
            fig.update_traces(marker_color='#a78bfa', texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(showgrid=False, color='white', title='Quarter'),
                yaxis=dict(gridcolor='#333333', color='white', title='Avg Transactions'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Transaction type distribution pie chart
            type_query = f"""
            SELECT 
                transaction_type,
                SUM(transaction_count) as total_trans
            FROM aggregated_transaction
            WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
            GROUP BY transaction_type
            ORDER BY total_trans DESC
            """
            df_types = qe.execute_query(conn, type_query)
            
            fig = px.pie(
                df_types,
                values='total_trans',
                names='transaction_type',
                title='Transaction Distribution by Type',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                showlegend=False,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Question 2: Transaction value analysis
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                💡 Additional Insight: Transaction Value Patterns by Type and Season
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                df_seasonal,
                x='quarter_label',
                y='avg_amount',
                title='Average Transaction Amount by Quarter',
                markers=True
            )
            fig.update_traces(line_color='#10b981', line_width=3, marker=dict(size=10))
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(showgrid=False, color='white', title='Quarter'),
                yaxis=dict(gridcolor='#333333', color='white', title='Avg Amount'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Average amount per transaction type
            amt_by_type_query = f"""
            SELECT 
                transaction_type,
                ROUND(AVG(transaction_amount), 2) as avg_amount
            FROM aggregated_transaction
            WHERE 1=1 {state_condition} {year_condition} {quarter_condition}
            GROUP BY transaction_type
            ORDER BY avg_amount DESC
            """
            df_amt = qe.execute_query(conn, amt_by_type_query)
            
            fig = px.bar(
                df_amt,
                x='transaction_type',
                y='avg_amount',
                title='Average Amount by Transaction Type',
                color='avg_amount',
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(gridcolor='#333333', color='white', title='Avg Amount (₹)'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=80)
            )
            st.plotly_chart(fig, use_container_width=True)
        
    elif case_id == "case_2":
        # Question 1: Which device brands dominate the digital payment market?
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                ❓ Question 1: Which device brands dominate the digital payment market?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        brand_query = f"""
        SELECT 
            brand,
            SUM(registered_users) as total_users,
            COUNT(DISTINCT state) as states_present
        FROM aggregated_user
        WHERE brand != 'Total' {state_condition} {year_condition} {quarter_condition}
        GROUP BY brand
        ORDER BY total_users DESC
        LIMIT 15
        """
        df_brands = qe.execute_query(conn, brand_query)
        df_brands['market_share'] = _safe_numeric_round(
            df_brands['total_users'] / df_brands['total_users'].sum() * 100,
            2
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Market share pie chart
            fig = px.pie(
                df_brands.head(10),
                values='total_users',
                names='brand',
                title='Top 10 Device Brands by User Base',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                showlegend=True,
                legend=dict(font=dict(color='white', size=9)),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart of market share
            fig = px.bar(
                df_brands.head(10),
                x='brand',
                y='market_share',
                title='Market Share % by Brand',
                color='market_share',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(gridcolor='#333333', color='white', title='Market Share (%)'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Question 4: Are there emerging device brands gaining market share?
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                ❓ Question 4: Are there emerging device brands gaining market share?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        growth_query = f"""
        SELECT 
            year,
            brand,
            SUM(registered_users) as users
        FROM aggregated_user
        WHERE brand != 'Total' {state_condition} {year_condition} {quarter_condition}
        GROUP BY year, brand
        ORDER BY year, users DESC
        """
        df = qe.execute_query(conn, growth_query)
        
        top_brands = df.groupby('brand')['users'].sum().nlargest(8).index
        df_filtered = df[df['brand'].isin(top_brands)]
        
        fig = px.line(
            df_filtered,
            x='year',
            y='users',
            color='brand',
            title='Top 8 Device Brands - User Growth Over Time',
            markers=True
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=14, color='white'),
            xaxis=dict(showgrid=False, color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            legend=dict(font=dict(color='white'), title_text=''),
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Cases 4, 5, 7: Market expansion, user growth, and state analysis
        if case_id == "case_4":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                    ❓ Question 1: What are the transaction volume trends across states?
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif case_id == "case_5":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                    ❓ Question 1: What are the user growth trends across different periods?
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif case_id == "case_7":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                    ❓ Question 4: How do year-over-year comparisons look across states?
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        query = f"""
        SELECT 
            year,
            quarter,
            SUM(transaction_count) as transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY year, quarter
        ORDER BY year, quarter
        """
        df = qe.execute_query(conn, query)
        df['period'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        
        # Calculate QoQ growth
        df['prev_trans'] = df['transactions'].shift(1)
        df['qoq_growth'] = _safe_numeric_round(
            (df['transactions'] - df['prev_trans']) / df['prev_trans'] * 100,
            2
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df,
                x='period',
                y='transactions',
                title='Quarterly Transaction Volume',
                color='transactions',
                color_continuous_scale='Purples'
            )
            fig.update_traces(marker_line_color='#667eea', marker_line_width=1)
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white'),
                yaxis=dict(gridcolor='#333333', color='white'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # QoQ growth rate
            df_growth = df[df['qoq_growth'].notna()]
            fig = px.line(
                df_growth,
                x='period',
                y='qoq_growth',
                title='Quarter-over-Quarter Growth Rate (%)',
                markers=True
            )
            fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
            fig.update_traces(line_color='#10b981', line_width=3, marker=dict(size=8))
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white'),
                yaxis=dict(gridcolor='#333333', color='white', title='Growth (%)'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Case 4: Emerging markets analysis
        if case_id == "case_4":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
                <p style="margin: 0; color: #000000; font-weight: 600; font-size: 1rem;">
                    ❓ Question 2: Where are the emerging high-growth markets?
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            emerging_query = f"""
            WITH yearly_state AS (
                SELECT 
                    state,
                    year,
                    SUM(transaction_count) as transactions
                FROM aggregated_transaction
                WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
                GROUP BY state, year
            ),
            growth_calc AS (
                SELECT 
                    state,
                    year,
                    transactions,
                    LAG(transactions) OVER (PARTITION BY state ORDER BY year) as prev_year
                FROM yearly_state
            ),
            avg_growth AS (
                SELECT 
                    state,
                    AVG((transactions - prev_year) * 100.0 / prev_year) as avg_growth_rate,
                    MAX(transactions) as latest_volume
                FROM growth_calc
                WHERE prev_year IS NOT NULL
                GROUP BY state
            )
            SELECT 
                state,
                ROUND(avg_growth_rate, 2) as avg_growth_rate,
                latest_volume
            FROM avg_growth
            WHERE avg_growth_rate > 10 AND latest_volume < (SELECT AVG(latest_volume) * 1.5 FROM avg_growth)
            ORDER BY avg_growth_rate DESC
            LIMIT 15
            """
            df_emerging = qe.execute_query(conn, emerging_query)
            
            if not df_emerging.empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    df_emerging['state_name'] = df_emerging['state'].apply(normalize_state_name)
                    fig = px.scatter(
                        df_emerging,
                        x='latest_volume',
                        y='avg_growth_rate',
                        size='latest_volume',
                        color='avg_growth_rate',
                        hover_name='state_name',
                        hover_data={
                            'state': False,
                            'state_name': False,
                            'latest_volume': ':.2f',
                            'avg_growth_rate': ':.2f'
                        },
                        title='Emerging Markets: High Growth + Moderate Volume',
                        labels={'latest_volume': 'Current Transaction Volume', 'avg_growth_rate': 'Avg Growth Rate (%)'},
                        color_continuous_scale='Viridis'
                    )
                    fig.update_traces(
                        hovertemplate='<b>%{hovertext}</b><br>Volume: %{x:.2f}<br>Avg Growth: %{y:.2f}%<extra></extra>'
                    )
                    fig.update_layout(
                        plot_bgcolor='#1a1a1a',
                        paper_bgcolor='#1a1a1a',
                        font=dict(color='white', family='Poppins, sans-serif'),
                        title_font=dict(size=14, color='white'),
                        xaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                        yaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                        margin=dict(l=40, r=20, t=50, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("""
                    <div style="background: #f8fafc; border-left: 3px solid #10b981; padding: 0.75rem 0.9rem; border-radius: 6px; margin-top: 0.75rem;">
                        <p style="color: #111827; font-size: 0.85rem; margin: 0; line-height: 1.5;">
                            <strong>How to read:</strong> top-right bubbles indicate stronger emerging markets (higher growth with higher current volume),
                            while top-left bubbles are early-stage high-growth opportunities.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                    st.markdown("**🎯 Top Emerging Markets:**")
                    for rank, row in enumerate(df_emerging.head(8).itertuples(index=False), start=1):
                        st.markdown(f"""
                        <div style="background: #dcfce7; border-left: 3px solid #10b981; padding: 0.85rem 0.9rem; margin-bottom: 0.55rem; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.75rem;">
                                <div style="min-width: 0;">
                                    <p style="color: #ffffff; font-size: 0.75rem; margin: 0;">Rank #{rank}</p>
                                    <p style="color: #ffffff; font-size: 0.95rem; font-weight: 600; margin: 0.2rem 0 0 0; word-break: break-word;">
                                        {normalize_state_name(row.state)}
                                    </p>
                                </div>
                                <div style="text-align: right; white-space: nowrap;">
                                    <p style="color: #10b981; font-size: 0.85rem; font-weight: 600; margin: 0;">
                                        {float(row.avg_growth_rate):.2f}%
                                    </p>
                                    <p style="color: #ffffff; font-size: 0.72rem; margin: 0.15rem 0 0 0;">Avg Growth</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No emerging markets identified with current criteria.")
        
        # Case 5: User retention patterns
        elif case_id == "case_5":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
                <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                    ❓ Question 3: How do user retention patterns vary?
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            user_growth_year_condition = year_condition
            selected_growth_year = None
            if year_filter != "All":
                selected_growth_year = int(year_filter)
                user_growth_year_condition = f"AND year IN ({selected_growth_year - 1}, {selected_growth_year})"

            retention_query = f"""
            SELECT 
                state,
                year,
                SUM(registered_users) as users
            FROM aggregated_user
            WHERE brand = 'Total' {state_scope_condition} {user_growth_year_condition} {quarter_condition}
            GROUP BY state, year
            ORDER BY state, year
            """
            df_users = qe.execute_query(conn, retention_query)
            
            # Calculate year-over-year user growth
            df_users['prev_users'] = df_users.groupby('state')['users'].shift(1)
            df_users['user_growth'] = _safe_numeric_round(
                (df_users['users'] - df_users['prev_users']) / df_users['prev_users'] * 100,
                2
            )
            
            # Top states by user growth
            latest_year = selected_growth_year if selected_growth_year is not None else df_users['year'].max()
            df_latest_growth = df_users[df_users['year'] == latest_year].dropna(subset=['user_growth']).sort_values('user_growth', ascending=False).head(15)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if df_latest_growth.empty:
                    st.info("No user growth data available for the selected year and filters.")
                else:
                    fig = px.bar(
                        df_latest_growth,
                        x='state',
                        y='user_growth',
                        title=f'Top 15 States by User Growth Rate ({latest_year})',
                        color='user_growth',
                        labels={
                            'state': 'State',
                            'user_growth': 'User Growth (%)'
                        },
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(
                        plot_bgcolor='#1a1a1a',
                        paper_bgcolor='#1a1a1a',
                        font=dict(color='white', family='Poppins, sans-serif'),
                        title_font=dict(size=14, color='white'),
                        xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                        yaxis=dict(gridcolor='#333333', color='white', title='Growth Rate (%)'),
                        showlegend=False,
                        margin=dict(l=40, r=20, t=50, b=120)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Show states with consistent growth
                consistency_query = f"""
                WITH yearly_growth AS (
                    SELECT 
                        state,
                        year,
                        SUM(registered_users) as users,
                        LAG(SUM(registered_users)) OVER (PARTITION BY state ORDER BY year) as prev_users
                    FROM aggregated_user
                    WHERE brand = 'Total' {state_scope_condition} {year_condition} {quarter_condition}
                    GROUP BY state, year
                ),
                growth_rates AS (
                    SELECT 
                        state,
                        year,
                        CASE WHEN prev_users > 0 THEN ((users - prev_users) * 100.0 / prev_users) ELSE 0 END as growth_rate
                    FROM yearly_growth
                    WHERE prev_users IS NOT NULL
                )
                SELECT 
                    state,
                    COUNT(CASE WHEN growth_rate > 0 THEN 1 END) as positive_years,
                    ROUND(AVG(growth_rate), 2) as avg_growth
                FROM growth_rates
                GROUP BY state
                HAVING positive_years >= 2
                ORDER BY avg_growth DESC
                LIMIT 10
                """
                df_consistent = qe.execute_query(conn, consistency_query)
                
                fig = px.bar(
                    df_consistent,
                    x='state',
                    y='avg_growth',
                    title='States with Consistent User Growth',
                    color='positive_years',
                    labels={
                        'state': 'State',
                        'avg_growth': 'Average Growth (%)',
                        'positive_years': 'Positive Years'
                    },
                    color_continuous_scale='Greens'
                )
                fig.update_layout(
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    font=dict(color='white', family='Poppins, sans-serif'),
                    title_font=dict(size=14, color='white'),
                    xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                    yaxis=dict(gridcolor='#333333', color='white', title='Avg Growth (%)'),
                    coloraxis_colorbar=dict(title='Positive Years'),
                    margin=dict(l=40, r=20, t=50, b=120)
                )
                st.plotly_chart(fig, use_container_width=True)

def show_geographical_section(case_id, conn, year_filter, quarter_filter, state_filter):
    """Display geographical analysis"""
    st.markdown("#### 🗺️ Geographical Analysis")
    
    # Add case-specific question headers
    if case_id == "case_1":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                💡 Insight: Payment Type Preferences Vary Significantly by State
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif case_id == "case_2":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                ❓ Question 2: How does device preference vary by region?
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif case_id == "case_4":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                ❓ Question 3 & 4: Digital payment penetration & expansion opportunities
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif case_id == "case_5":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                ❓ Question 2: Which states have the highest user engagement?
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif case_id == "case_7":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                ❓ Question 1 & 3: Top states by transaction volume & performance scorecard
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    year_condition = f"AND year = {year_filter}" if year_filter != "All" else "AND year >= 2022"
    quarter_condition = f"AND quarter = {quarter_filter}" if quarter_filter != "All" else ""
    state_scope_condition = f"AND state = '{state_filter}'" if state_filter != "All India" else "AND state != 'All India'"
    
    # Case-specific geographic analysis
    if case_id == "case_1":
        # Focus on transaction type distribution by state
        query = f"""
        SELECT 
            state,
            transaction_type,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY state, transaction_type
        """
        df_detail = qe.execute_query(conn, query)

        state_totals = (
            df_detail.groupby('state', as_index=False)['total_transactions']
            .sum()
            .sort_values('total_transactions', ascending=False)
        )
        top_states = state_totals.head(15)['state'].tolist()
        df_full_distribution = df_detail[df_detail['state'].isin(top_states)]

        st.markdown("**💳 Full Payment Type Distribution by State**")
        fig = px.bar(
            df_full_distribution,
            x='state',
            y='total_transactions',
            color='transaction_type',
            barmode='stack',
            title='Transaction Type Distribution across Top 15 States',
            labels={'total_transactions': 'Transactions', 'state': 'State', 'transaction_type': 'Type'},
            category_orders={'state': top_states}
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=14, color='white'),
            xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
            yaxis=dict(gridcolor='#333333', color='white'),
            legend=dict(font=dict(color='white'), title_text='Type'),
            margin=dict(l=40, r=20, t=50, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif case_id == "case_2":
        # Focus on device brand distribution by state
        query = f"""
        SELECT 
            state,
            brand,
            SUM(registered_users) as users
        FROM aggregated_user
        WHERE brand != 'Total' {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY state, brand
        """
        df_brand_state = qe.execute_query(conn, query)

        if df_brand_state is not None and not df_brand_state.empty:
            top_states = (
                df_brand_state.groupby('state', as_index=False)['users']
                .sum()
                .sort_values('users', ascending=False)
                .head(10)['state']
                .tolist()
            )

            top_brands = (
                df_brand_state.groupby('brand', as_index=False)['users']
                .sum()
                .sort_values('users', ascending=False)
                .head(5)['brand']
                .tolist()
            )

            df_multi_brand = df_brand_state[
                df_brand_state['state'].isin(top_states) &
                df_brand_state['brand'].isin(top_brands)
            ]

            state_order = (
                df_multi_brand.groupby('state', as_index=False)['users']
                .sum()
                .sort_values('users', ascending=False)['state']
                .tolist()
            )

            st.markdown("**📱 Device Preference by Region (Multi-Brand View)**")
            fig = px.bar(
                df_multi_brand,
                x='state',
                y='users',
                color='brand',
                barmode='group',
                title='Top 5 Device Brands across Top 10 States',
                labels={'users': 'Registered Users', 'state': 'State', 'brand': 'Brand'},
                category_orders={'state': state_order}
            )
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(gridcolor='#333333', color='white', title='Registered Users'),
                legend=dict(font=dict(color='white'), title_text='Brand'),
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No regional device preference data available for selected filters")
        
        # Brand diversity by state
        brand_diversity = df_brand_state.groupby('state').agg({
            'brand': 'count',
            'users': 'sum'
        }).reset_index()
        brand_diversity.columns = ['state', 'brand_count', 'total_users']

        concentration_df = df_brand_state.copy()
        state_totals = concentration_df.groupby('state')['users'].sum().rename('state_total')
        concentration_df = concentration_df.merge(state_totals, on='state', how='left')
        concentration_df['brand_share_pct'] = _safe_numeric_round(
            concentration_df['users'] * 100.0 / concentration_df['state_total'],
            2
        )

        top_brand_share = concentration_df.groupby('state', as_index=False)['brand_share_pct'].max()
        top_brand_share.columns = ['state', 'top_brand_share_pct']

        hhi_df = concentration_df.groupby('state', as_index=False)['brand_share_pct'].apply(
            lambda s: (s ** 2).sum()
        )
        hhi_df.columns = ['state', 'hhi']

        brand_diversity = brand_diversity.merge(top_brand_share, on='state', how='left')
        brand_diversity = brand_diversity.merge(hhi_df, on='state', how='left')
        brand_diversity = brand_diversity.sort_values('total_users', ascending=False).head(15)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🎯 Brand Diversity Index**")
            if brand_diversity is not None and not brand_diversity.empty:
                # Ensure data types are numeric
                brand_diversity['total_users'] = pd.to_numeric(brand_diversity['total_users'], errors='coerce')
                brand_diversity['brand_count'] = pd.to_numeric(brand_diversity['brand_count'], errors='coerce')
                brand_diversity['top_brand_share_pct'] = pd.to_numeric(brand_diversity['top_brand_share_pct'], errors='coerce')
                brand_diversity['hhi'] = pd.to_numeric(brand_diversity['hhi'], errors='coerce')
                brand_diversity = brand_diversity.dropna()
                
                if not brand_diversity.empty:
                    fig = px.scatter(
                        brand_diversity,
                        x='total_users',
                        y='brand_count',
                        size='total_users',
                        color='top_brand_share_pct',
                        hover_data=['state', 'top_brand_share_pct', 'hhi'],
                        title='Brand Diversity vs User Base',
                        labels={'total_users': 'Total Users', 'brand_count': 'Number of Brands', 'top_brand_share_pct': 'Top Brand Share (%)'},
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(
                        plot_bgcolor='#1a1a1a',
                        paper_bgcolor='#1a1a1a',
                        font=dict(color='white', family='Poppins, sans-serif'),
                        title_font=dict(size=14, color='white'),
                        xaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                        yaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                        margin=dict(l=40, r=20, t=50, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No brand diversity data available")
            else:
                st.info("No brand diversity data available")
        
        with col2:
            st.markdown("**📊 Top States by User Base**")
            fig = px.bar(
                brand_diversity.head(10),
                x='state',
                y='total_users',
                title='Top 10 States by Total Users',
                color='total_users',
                color_continuous_scale='Purples'
            )
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(gridcolor='#333333', color='white'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)

        if brand_diversity is not None and not brand_diversity.empty:
            st.markdown("**📌 Brand Concentration Metrics**")
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            avg_top_share = brand_diversity['top_brand_share_pct'].mean()
            avg_hhi = brand_diversity['hhi'].mean()
            most_competitive_state = brand_diversity.sort_values('top_brand_share_pct', ascending=True).iloc[0]['state']

            with metric_col1:
                st.metric("Top Brand Share (Avg)", f"{avg_top_share:.2f}%")
            with metric_col2:
                st.metric("HHI (Avg)", f"{avg_hhi:.2f}")
            with metric_col3:
                st.metric("Most Competitive", normalize_state_name(most_competitive_state))
    
    elif case_id == "case_4":
        # Focus on expansion opportunities - penetration and growth potential
        query = f"""
        WITH state_metrics AS (
            SELECT 
                state,
                SUM(transaction_count) as total_transactions,
                ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions,
                COUNT(DISTINCT year || '-' || quarter) as periods
            FROM aggregated_transaction
            WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
            GROUP BY state
        ),
        user_metrics AS (
            SELECT 
                state,
                SUM(registered_users) as total_users
            FROM aggregated_user
            WHERE brand = 'Total' {state_scope_condition} {year_condition} {quarter_condition}
            GROUP BY state
        )
        SELECT 
            s.state,
            s.total_transactions,
            s.amount_billions,
            COALESCE(u.total_users, 0) as users,
            CASE WHEN u.total_users > 0 THEN ROUND(s.total_transactions * 1.0 / u.total_users, 2) ELSE 0 END as trans_per_user
        FROM state_metrics s
        LEFT JOIN user_metrics u ON s.state = u.state
        ORDER BY s.total_transactions DESC
        """
        df_expansion = qe.execute_query(conn, query)
        
        # High volume states
        df_high_vol = df_expansion.head(10)
        
        # Medium volume, high engagement (expansion opportunity)
        df_expansion['opportunity_score'] = df_expansion['trans_per_user'] * (df_expansion['total_transactions'] / df_expansion['total_transactions'].max())
        df_opportunity = df_expansion[(df_expansion['total_transactions'] < df_expansion['total_transactions'].quantile(0.5)) & 
                                      (df_expansion['trans_per_user'] > df_expansion['trans_per_user'].median())].sort_values('opportunity_score', ascending=False).head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Established Markets (High Volume)**")
            fig = px.bar(
                df_high_vol,
                x='state',
                y='total_transactions',
                title='Top 10 High-Volume States',
                color='trans_per_user',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(gridcolor='#333333', color='white', title='Transactions'),
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🎯 Expansion Opportunity States**")
            if not df_opportunity.empty:
                fig = px.bar(
                    df_opportunity,
                    x='state',
                    y='trans_per_user',
                    title='High Engagement, Moderate Volume States',
                    color='opportunity_score',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    font=dict(color='white', family='Poppins, sans-serif'),
                    title_font=dict(size=14, color='white'),
                    xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                    yaxis=dict(gridcolor='#333333', color='white', title='Trans/User'),
                    margin=dict(l=40, r=20, t=50, b=100)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No clear expansion opportunities identified in current data")
        
        # Penetration heatmap
        st.markdown("**💡 Transaction Penetration Analysis**")
        if df_expansion is not None and not df_expansion.empty:
            # Ensure data types are numeric
            df_expansion['users'] = pd.to_numeric(df_expansion['users'], errors='coerce')
            df_expansion['total_transactions'] = pd.to_numeric(df_expansion['total_transactions'], errors='coerce')
            df_expansion['trans_per_user'] = pd.to_numeric(df_expansion['trans_per_user'], errors='coerce')
            df_expansion = df_expansion.dropna()
            
            if not df_expansion.empty:
                fig = px.scatter(
                    df_expansion.head(20),
                    x='users',
                    y='total_transactions',
                    size='trans_per_user',
                    color='trans_per_user',
                    hover_data=['state'],
                    title='User Base vs Transaction Volume (Bubble size = Transactions per User)',
                    labels={'users': 'Total Users', 'total_transactions': 'Total Transactions'},
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    font=dict(color='white', family='Poppins, sans-serif'),
                    title_font=dict(size=14, color='white'),
                    xaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                    yaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
                    margin=dict(l=40, r=20, t=50, b=40)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No penetration data available")
        else:
            st.info("No penetration data available")
    
    elif case_id == "case_5":
        # Focus on user engagement metrics by state
        query = f"""
        SELECT 
            state,
            year,
            SUM(registered_users) as users
        FROM aggregated_user
        WHERE brand = 'Total' {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY state, year
        """
        df_users = qe.execute_query(conn, query)
        
        # Calculate engagement score (total users)
        df_engagement = df_users.groupby('state')['users'].sum().reset_index()
        df_engagement.columns = ['state', 'total_users']
        df_engagement = df_engagement.sort_values('total_users', ascending=False)
        
        user_growth_year_condition = year_condition
        selected_growth_year = None
        if year_filter != "All":
            selected_growth_year = int(year_filter)
            user_growth_year_condition = f"AND year IN ({selected_growth_year - 1}, {selected_growth_year})"

        growth_query = f"""
        SELECT 
            state,
            year,
            SUM(registered_users) as users
        FROM aggregated_user
        WHERE brand = 'Total' {state_scope_condition} {user_growth_year_condition} {quarter_condition}
        GROUP BY state, year
        """
        df_users_growth = qe.execute_query(conn, growth_query)

        # User growth by state
        df_users_growth['prev_users'] = df_users_growth.groupby('state')['users'].shift(1)
        df_users_growth['growth'] = _safe_numeric_round(
            (df_users_growth['users'] - df_users_growth['prev_users']) / df_users_growth['prev_users'] * 100,
            2
        )

        latest_year = selected_growth_year if selected_growth_year is not None else df_users_growth['year'].max()
        df_latest_growth = df_users_growth[df_users_growth['year'] == latest_year].dropna(subset=['growth']).sort_values('growth', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👥 Top 15 States by User Base**")
            fig = px.bar(
                df_engagement.head(15),
                x='state',
                y='total_users',
                title='Highest User Engagement States',
                color='total_users',
                color_continuous_scale='Purples'
            )
            fig.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(gridcolor='#333333', color='white', title='Users'),
                showlegend=False,
                margin=dict(l=40, r=20, t=50, b=100)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"**📈 Fastest Growing States ({latest_year})**")
            if df_latest_growth.empty:
                st.info("No user growth data available for the selected year and filters.")
            else:
                fig = px.bar(
                    df_latest_growth.head(15),
                    x='state',
                    y='growth',
                    title=f'Top 15 User Growth Leaders',
                    color='growth',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    font=dict(color='white', family='Poppins, sans-serif'),
                    title_font=dict(size=14, color='white'),
                    xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                    yaxis=dict(gridcolor='#333333', color='white', title='Growth (%)'),
                    showlegend=False,
                    margin=dict(l=40, r=20, t=50, b=100)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    elif case_id == "case_7":
        # This case specifically needs top states analysis - keep enhanced version
        query = f"""
        SELECT 
            state,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY state
        ORDER BY total_transactions DESC
        """
        df_all = qe.execute_query(conn, query)
        df_all['pct_share'] = _safe_numeric_round(
            df_all['total_transactions'] / df_all['total_transactions'].sum() * 100,
            2
        )
        
        # Top 10 states with metrics
        st.markdown("**🏆 Top 10 States Performance Dashboard**")
        
        df_top10 = df_all.head(10)
        
        # Create cards for top 10
        cols = st.columns(2)
        for idx, row in df_top10.iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ADD8E6 0%, #87CEEB 100%); border-left: 4px solid #0066cc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="color: #003d99; font-size: 0.9rem; margin: 0; font-weight: bold;">#{idx+1}</p>
                            <h4 style="color: #000033; margin: 0.25rem 0; font-weight: 700;">{normalize_state_name(row['state'])}</h4>
                            <p style="color: #001a4d; font-size: 0.85rem; margin: 0.25rem 0; font-weight: 500;">
                                {format_large_number(row['total_transactions'])} transactions<br>
                                ₹{row['amount_billions']:.2f}B amount<br>
                                <span style="color: #004d00; font-weight: 600;">{row['pct_share']:.2f}% market share</span>
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Comparison chart
        st.markdown("**📊 Performance Comparison**")
        fig = px.scatter(
            df_top10,
            x='total_transactions',
            y='amount_billions',
            size='pct_share',
            color='pct_share',
            hover_name='state',
            title='Top 10 States: Transaction Volume vs Value',
            labels={
                'total_transactions': 'Transactions',
                'amount_billions': 'Amount (₹ Billions)',
                'pct_share': 'Market Share (%)'
            },
            color_continuous_scale='Blues'
        )
        fig.add_trace(
            go.Scatter(
                x=df_top10['total_transactions'],
                y=df_top10['amount_billions'],
                mode='text',
                text=df_top10['state'].apply(normalize_state_name),
                textposition='top center',
                textfont=dict(color='white', size=10),
                hoverinfo='skip',
                showlegend=False
            )
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=14, color='white'),
            xaxis=dict(showgrid=True, gridcolor='#333333', color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            coloraxis_colorbar=dict(title='Market Share (%)'),
            margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Default generic view for any other cases
        query = f"""
        SELECT 
            state,
            SUM(transaction_count) as total_transactions,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY state
        ORDER BY total_transactions DESC
        """
        df_all = qe.execute_query(conn, query)
        
        df_top15 = df_all.head(15)
        
        fig = px.bar(
            df_top15,
            x='state',
            y='total_transactions',
            title='Top 15 States by Transaction Volume',
            color='total_transactions',
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white', family='Poppins, sans-serif'),
            title_font=dict(size=16, color='white'),
            xaxis=dict(tickangle=45, showgrid=False, color='white'),
            yaxis=dict(gridcolor='#333333', color='white'),
            showlegend=False,
            margin=dict(l=40, r=20, t=50, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Case 1 specific: States with declining transactions (Question 4)
    if case_id == "case_1":
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                ❓ Question 4: Which states show declining transaction trends?
            </p>
        </div>
        """, unsafe_allow_html=True)

        decline_year_condition = year_condition
        selected_decline_year = None
        if year_filter != "All":
            selected_decline_year = int(year_filter)
            decline_year_condition = f"AND year IN ({selected_decline_year - 1}, {selected_decline_year})"
        
        declining_query = f"""
        WITH yearly_state AS (
            SELECT 
                state,
                year,
                SUM(transaction_count) as transactions
            FROM aggregated_transaction
            WHERE 1=1 {state_scope_condition} {decline_year_condition} {quarter_condition}
            GROUP BY state, year
        ),
        growth_calc AS (
            SELECT 
                state,
                year,
                transactions,
                LAG(transactions) OVER (PARTITION BY state ORDER BY year) as prev_year_trans
            FROM yearly_state
        ),
        declining_ranked AS (
            SELECT
                state,
                year,
                transactions,
                prev_year_trans,
                ROUND((transactions - prev_year_trans) * 100.0 / prev_year_trans, 2) as growth_rate,
                ROW_NUMBER() OVER (
                    PARTITION BY state
                    ORDER BY ((transactions - prev_year_trans) * 100.0 / prev_year_trans) ASC
                ) as rn
            FROM growth_calc
            WHERE prev_year_trans IS NOT NULL
        )
        SELECT 
            state,
            year,
            transactions,
            prev_year_trans,
            growth_rate
        FROM declining_ranked
        WHERE rn = 1 AND growth_rate < 0
        ORDER BY growth_rate ASC
        LIMIT 10
        """
        
        df_declining = qe.execute_query(conn, declining_query)
        if selected_decline_year is not None and not df_declining.empty:
            df_declining = df_declining[df_declining['year'] == selected_decline_year]
        df_negative = df_declining

        decline_heatmap_query = f"""
        WITH yearly_state AS (
            SELECT 
                state,
                year,
                SUM(transaction_count) as transactions
            FROM aggregated_transaction
            WHERE 1=1 {state_scope_condition} {decline_year_condition} {quarter_condition}
            GROUP BY state, year
        ),
        growth_calc AS (
            SELECT 
                state,
                year,
                transactions,
                LAG(transactions) OVER (PARTITION BY state ORDER BY year) as prev_year_trans
            FROM yearly_state
        )
        SELECT
            state,
            year,
            ROUND((transactions - prev_year_trans) * 100.0 / prev_year_trans, 2) as growth_rate
        FROM growth_calc
        WHERE prev_year_trans IS NOT NULL
        """
        df_growth_heatmap = qe.execute_query(conn, decline_heatmap_query)
        
        if df_growth_heatmap is not None and not df_growth_heatmap.empty:
            df_period = df_growth_heatmap.copy()

            if selected_decline_year is not None:
                analysis_year = selected_decline_year
                df_period = df_period[df_period['year'] == analysis_year]
                chart_title = f'All States YoY Growth ({analysis_year})'
                y_column = 'state_label'
            else:
                analysis_year = None
                chart_title = 'All States YoY Growth (All Years)'
                df_period['year'] = pd.to_numeric(df_period['year'], errors='coerce')
                df_period = df_period.dropna(subset=['year'])
                df_period['year'] = df_period['year'].astype(int)
                y_column = 'state_year'

            if not df_period.empty:
                df_period['state_label'] = df_period['state'].apply(normalize_state_name)
                if analysis_year is None:
                    df_period['state_year'] = df_period.apply(
                        lambda row: f"{row['state_label']} ({int(row['year'])})",
                        axis=1
                    )
                df_period['trend'] = df_period['growth_rate'].apply(
                    lambda value: 'Decline' if value < 0 else ('Growth' if value > 0 else 'Flat')
                )
                df_period = df_period.sort_values('growth_rate', ascending=True)

                col1, col2 = st.columns([3, 1])

                with col1:
                    fig = px.bar(
                        df_period,
                        x='growth_rate',
                        y=y_column,
                        orientation='h',
                        color='trend',
                        title=chart_title,
                        labels={'growth_rate': 'YoY Growth Rate (%)', y_column: 'State'},
                        color_discrete_map={
                            'Decline': '#ef4444',
                            'Growth': '#22c55e',
                            'Flat': '#94a3b8'
                        }
                    )
                    fig.add_vline(x=0, line_dash='dash', line_color='white', opacity=0.6)
                    fig.update_layout(
                        plot_bgcolor='#1a1a1a',
                        paper_bgcolor='#1a1a1a',
                        font=dict(color='white', family='Poppins, sans-serif'),
                        title_font=dict(size=14, color='white'),
                        xaxis=dict(showgrid=True, gridcolor='#333333', color='white', title='YoY Growth (%)'),
                        yaxis=dict(showgrid=False, color='white', title=''),
                        legend=dict(font=dict(color='white'), title_text='Trend'),
                        margin=dict(l=40, r=20, t=50, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    total_states = len(df_period) if analysis_year is None else len(df_period)
                    declines_count = int((df_period['growth_rate'] < 0).sum())
                    growth_count = int((df_period['growth_rate'] > 0).sum())
                    flat_count = int((df_period['growth_rate'] == 0).sum())

                    metric_label = 'State-Year Entries' if analysis_year is None else 'States Analyzed'
                    st.metric(metric_label, f'{total_states}')
                    st.metric('Declining States', f'{declines_count}')
                    st.metric('Growing States', f'{growth_count}')
                    st.metric('Flat States', f'{flat_count}')

                states_with_decline = (
                    df_growth_heatmap[df_growth_heatmap['growth_rate'] < 0]
                    .groupby('state')['growth_rate']
                    .min()
                    .sort_values(ascending=True)
                    .head(12)
                    .index
                    .tolist()
                )

                if states_with_decline:
                    df_heatmap = df_growth_heatmap[df_growth_heatmap['state'].isin(states_with_decline)].copy()
                    state_label_map = {state: normalize_state_name(state) for state in states_with_decline}
                    ordered_labels = [state_label_map[state] for state in states_with_decline]
                    df_heatmap['state_label'] = df_heatmap['state'].map(state_label_map)
                    df_heatmap['year'] = pd.to_numeric(df_heatmap['year'], errors='coerce').astype('Int64')
                    df_heatmap = df_heatmap.dropna(subset=['year'])
                    df_heatmap['year_label'] = df_heatmap['year'].astype(int).astype(str)

                    year_order = sorted(df_heatmap['year_label'].unique(), key=lambda value: int(value))

                    heatmap_pivot = df_heatmap.pivot(
                        index='state_label',
                        columns='year_label',
                        values='growth_rate'
                    ).reindex(ordered_labels)
                    heatmap_pivot = heatmap_pivot.reindex(columns=year_order)

                    fig_heatmap = px.imshow(
                        heatmap_pivot,
                        color_continuous_scale='RdYlGn',
                        aspect='auto',
                        title='Year-wise Growth Pattern (Declining States)',
                        labels=dict(x='Year', y='State', color='Growth %')
                    )

                    negative_text = heatmap_pivot.apply(
                        lambda row: row.map(
                            lambda value: f"{value:.2f}%" if pd.notna(value) and value < 0 else ""
                        ),
                        axis=1
                    )
                    fig_heatmap.update_traces(
                        text=negative_text.values,
                        texttemplate='%{text}',
                        textfont=dict(color='white', size=10)
                    )

                    negative_points = (
                        heatmap_pivot.stack()
                        .reset_index(name='growth_rate')
                    )
                    negative_points = negative_points[negative_points['growth_rate'] < 0]

                    if not negative_points.empty:
                        fig_heatmap.add_trace(
                            go.Scatter(
                                x=negative_points['year_label'],
                                y=negative_points['state_label'],
                                mode='markers',
                                marker=dict(
                                    symbol='square-open',
                                    size=20,
                                    color='rgba(0,0,0,0)',
                                    line=dict(color='#ef4444', width=2)
                                ),
                                hoverinfo='skip',
                                showlegend=False
                            )
                        )

                    fig_heatmap.update_layout(
                        plot_bgcolor='#1a1a1a',
                        paper_bgcolor='#1a1a1a',
                        font=dict(color='white', family='Poppins, sans-serif'),
                        title_font=dict(size=14, color='white'),
                        margin=dict(l=40, r=20, t=50, b=40)
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("No year-over-year growth data available for the selected filters.")
        else:
            st.info("No year-over-year growth data available for the selected filters.")
    
    # Case 7 specific: Transaction concentration analysis
    if case_id == "case_7":
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="margin: 0; color: white; font-weight: 600; font-size: 1rem;">
                ❓ Question 2: How concentrated is transaction activity?
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate concentration metrics
        total_trans = df_all['total_transactions'].sum()
        df_all['cumulative_pct'] = _safe_numeric_round(
            df_all['total_transactions'].cumsum() / total_trans * 100,
            2
        )
        df_all['pct_share'] = _safe_numeric_round(
            df_all['total_transactions'] / total_trans * 100,
            2
        )
        
        # Find states contributing to 80% of transactions
        top_80_count = len(df_all[df_all['cumulative_pct'] <= 80])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Pareto chart showing concentration
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_all['state'].head(20),
                y=df_all['pct_share'].head(20),
                name='State Share (%)',
                marker_color='#667eea',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=df_all['state'].head(20),
                y=df_all['cumulative_pct'].head(20),
                name='Cumulative %',
                marker_color='#10b981',
                line=dict(width=3),
                yaxis='y2'
            ))
            
            fig.add_hline(y=80, line_dash="dash", line_color="red", opacity=0.5, annotation_text="80%", yref='y2')
            
            fig.update_layout(
                title='Transaction Concentration (Pareto Analysis)',
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='white', family='Poppins, sans-serif'),
                title_font=dict(size=14, color='white'),
                xaxis=dict(tickangle=-45, showgrid=False, color='white', title=''),
                yaxis=dict(
                    title='Individual Share (%)',
                    gridcolor='#333333',
                    color='white',
                    side='left'
                ),
                yaxis2=dict(
                    title='Cumulative Share (%)',
                    overlaying='y',
                    side='right',
                    color='#10b981',
                    showgrid=False
                ),
                legend=dict(font=dict(color='white'), x=0.7, y=1),
                margin=dict(l=40, r=60, t=50, b=120)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            
            # Concentration metrics
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                <h3 style="color: white; font-size: 2rem; margin: 0;">{top_80_count}</h3>
                <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                    States contribute<br>80% of transactions
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            top3_share = df_all['pct_share'].head(3).sum()
            st.markdown(f"""
            <div style="background: #1f2937; border: 2px solid #667eea; padding: 1.5rem; border-radius: 12px;">
                <h3 style="color: white; font-size: 2rem; margin: 0;">{top3_share:.2f}%</h3>
                <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                    Top 3 states' share
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Concentration insights
        st.markdown("##### 💡 Concentration Insights")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: #ffcccc; border-left: 3px solid #cc0000; padding: 1rem; border-radius: 4px;">
                <strong style="color: #660000; font-size: 1rem;">High Concentration</strong><br>
                <span style="color: #990000; font-size: 0.9rem; font-weight: 500;">Top {top_80_count} states drive 80% volume</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #cce5ff; border-left: 3px solid #0033cc; padding: 1rem; border-radius: 4px;">
                <strong style="color: #003366; font-size: 1rem;">Market Leader</strong><br>
                <span style="color: #004d99; font-size: 0.9rem; font-weight: 500;">{normalize_state_name(df_all.iloc[0]['state'])} leads with {df_all.iloc[0]['pct_share']:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            low_share_count = len(df_all[df_all['pct_share'] < 1])
            st.markdown(f"""
            <div style="background: #fffacd; border-left: 3px solid #ccaa00; padding: 1rem; border-radius: 4px;">
                <strong style="color: #664d00; font-size: 1rem;">Opportunity States</strong><br>
                <span style="color: #996600; font-size: 0.9rem; font-weight: 500;">{low_share_count} states with <1% share</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Case-specific additional insights (only if valuable)
    if case_id == "case_7":
        st.markdown("---")
        st.markdown("#### 🔍 District-Level Analysis")
        st.info("💡 **Note:** District-level data is available for detailed drill-down analysis of top-performing states.")
        
        query_all = f"""
        SELECT 
            state,
            SUM(transaction_count) as total_transactions
        FROM aggregated_transaction
        WHERE 1=1 {state_scope_condition} {year_condition} {quarter_condition}
        GROUP BY state
        ORDER BY total_transactions DESC
        """
        df_all = qe.execute_query(conn, query_all)
        
        state_list = ["Select a state..."] + df_all['state'].head(10).tolist()
        selected_state = st.selectbox(
            "Choose State for District Analysis",
            state_list,
            key=f"district_state_{case_id}"
        )
        
        if selected_state != "Select a state...":
            district_df = get_district_data(conn, selected_state, year_condition)
            
            if district_df is not None and not district_df.empty:
                st.success(f"**{normalize_state_name(selected_state)}** - Top {len(district_df)} Districts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = create_district_bar_chart(district_df, selected_state, 'total_transactions')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = create_district_bar_chart(district_df, selected_state, 'amount_billions')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Top 5 Districts Detail
                st.markdown("##### 📊 Top 5 Districts")
                for idx, row in district_df.head(5).iterrows():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{idx+1}. {row['district'].title()}**")
                    with col2:
                        st.markdown(f"🔢 {format_large_number(row['total_transactions'])}")
                    with col3:
                        st.markdown(f"💰 ₹{format_large_number(row['amount_billions']*1e9)}")
            else:
                st.warning(f"No district data available for {normalize_state_name(selected_state)}")

def show_insights_section(case_id, case_data, conn):
    """Display insights and recommendations"""
    st.markdown("""
    <h3 style="color: #000000; font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 1rem 0;">💡 Key Insights & Question Summary</h3>
    """, unsafe_allow_html=True)
    
    # Show which questions were answered with references to tabs
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h4 style="color: #000000 !important; margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 700;">📋 Questions Addressed in This Analysis</h4>
    """, unsafe_allow_html=True)
    
    # Display the key questions for this case
    if case_data and 'key_questions' in case_data:
        for idx, question in enumerate(case_data['key_questions'], 1):
            # Map questions to tabs
            if case_id == "case_1":
                if idx == 1:
                    tab_ref = "📈 Trends Tab"
                elif idx == 2:
                    tab_ref = "📊 Overview Tab"
                elif idx == 3:
                    tab_ref = "📈 Trends Tab"
                else:
                    tab_ref = "🗺️ Geographic Tab"
            elif case_id == "case_2":
                if idx == 1:
                    tab_ref = "📈 Trends Tab"
                elif idx == 2:
                    tab_ref = "📈 Trends Tab"
                elif idx == 3:
                    tab_ref = "📊 Overview Tab"
                else:
                    tab_ref = "📈 Trends Tab"
            elif case_id == "case_4":
                if idx <= 2:
                    tab_ref = "📈 Trends Tab"
                else:
                    tab_ref = "🗺️ Geographic Tab"
            elif case_id == "case_5":
                if idx == 1:
                    tab_ref = "📈 Trends Tab"
                elif idx == 2:
                    tab_ref = "🗺️ Geographic Tab"
                else:
                    tab_ref = "📈 Trends Tab"
            elif case_id == "case_7":
                if idx in [1, 3]:
                    tab_ref = "🗺️ Geographic Tab"
                elif idx == 2:
                    tab_ref = "🗺️ Geographic Tab"
                else:
                    tab_ref = "📈 Trends Tab"
            else:
                tab_ref = "Multiple Tabs"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 8px;">
                <p style="color: #000000; margin: 0; font-size: 0.95rem;">
                    <strong>Q{idx}:</strong> {question} <span style="color: #fbbf24;">→ {tab_ref}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Now show the detailed insights
    st.markdown("---")
    st.markdown("""
    <h3 style="color: #000000; font-size: 1.5rem; font-weight: 700; margin: 1.5rem 0 1rem 0;">🎯 Detailed Insights</h3>
    """, unsafe_allow_html=True)
    
    if case_id == "case_1":
        query = """
        SELECT 
            transaction_type,
            SUM(transaction_count) as total,
            ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
        FROM aggregated_transaction
        WHERE state = 'All India' AND year >= 2022
        GROUP BY transaction_type
        ORDER BY amount_billions DESC
        """
        df = qe.execute_query(conn, query)
        
        st.markdown(f"""
        <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="color: #000000; margin: 0; font-weight: 600; font-size: 1rem;">
                ✓ <strong>Top Category:</strong> {df.iloc[0]['transaction_type']} with ₹{df.iloc[0]['amount_billions']:.2f}B
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="color: #000000; font-weight: 600; margin-bottom: 0.5rem;">📊 Key Findings:</p>
            <ul style="color: #000000; margin: 0;">
                <li>Peer-to-peer payments dominate by value</li>
                <li>Merchant payments lead by volume</li>
                <li>Consistent growth across all categories</li>
            </ul>
            <p style="color: #000000; font-weight: 600; margin: 1rem 0 0.5rem 0;">💡 Recommendations:</p>
            <ul style="color: #000000; margin: 0;">
                <li>Focus on merchant onboarding in tier-2/3 cities</li>
                <li>Enhance P2P features</li>
                <li>Promote recharge services during festive seasons</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    elif case_id == "case_2":
        query = """
        SELECT 
            brand,
            SUM(registered_users) as users
        FROM aggregated_user
        WHERE state = 'All India' AND brand != 'Total'
        GROUP BY brand
        ORDER BY users DESC
        LIMIT 5
        """
        df = qe.execute_query(conn, query)
        
        st.markdown(f"""
        <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="color: #000000; margin: 0; font-weight: 600; font-size: 1rem;">
                ✓ <strong>Leading Brand:</strong> {df.iloc[0]['brand']} with {df.iloc[0]['users'] / 1e6:.2f}M users
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **Key Findings:**
        - Top 3 brands dominate user base
        - Regional preferences vary significantly
        - Android ecosystem leads adoption
        
        **Recommendations:**
        - Optimize for top device brands
        - Target emerging device segments
        - Develop device-specific features
        """)
    
    else:
        st.markdown("""
        **Key Findings:**
        - Strong growth across major states
        - Urban centers drive transaction volume
        - Tier-2/3 cities show high growth potential
        
        **Recommendations:**
        - Focus on regional expansion
        - Tailor offerings for local markets
        - Invest in merchant ecosystem
        """)

if __name__ == "__main__":
    main()
