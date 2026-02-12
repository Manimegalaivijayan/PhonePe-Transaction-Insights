"""
Map Utilities for India Geographical Visualization
Provides interactive choropleth maps with state-level data
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# India state mapping (lowercase with hyphens to proper names)
STATE_NAME_MAPPING = {
    'andaman-&-nicobar-islands': 'Andaman & Nicobar',
    'andhra-pradesh': 'Andhra Pradesh',
    'arunachal-pradesh': 'Arunachal Pradesh',
    'assam': 'Assam',
    'bihar': 'Bihar',
    'chandigarh': 'Chandigarh',
    'chhattisgarh': 'Chhattisgarh',
    'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli and Daman and Diu',
    'delhi': 'Delhi',
    'goa': 'Goa',
    'gujarat': 'Gujarat',
    'haryana': 'Haryana',
    'himachal-pradesh': 'Himachal Pradesh',
    'jammu-&-kashmir': 'Jammu & Kashmir',
    'jharkhand': 'Jharkhand',
    'karnataka': 'Karnataka',
    'kerala': 'Kerala',
    'ladakh': 'Ladakh',
    'lakshadweep': 'Lakshadweep',
    'madhya-pradesh': 'Madhya Pradesh',
    'maharashtra': 'Maharashtra',
    'manipur': 'Manipur',
    'meghalaya': 'Meghalaya',
    'mizoram': 'Mizoram',
    'nagaland': 'Nagaland',
    'odisha': 'Odisha',
    'puducherry': 'Puducherry',
    'punjab': 'Punjab',
    'rajasthan': 'Rajasthan',
    'sikkim': 'Sikkim',
    'tamil-nadu': 'Tamil Nadu',
    'telangana': 'Telangana',
    'tripura': 'Tripura',
    'uttar-pradesh': 'Uttar Pradesh',
    'uttarakhand': 'Uttarakhand',
    'west-bengal': 'West Bengal'
}

# ISO codes for India states (for choropleth mapping)
STATE_ISO_MAPPING = {
    'Andaman & Nicobar': 'AN',
    'Andhra Pradesh': 'AP',
    'Arunachal Pradesh': 'AR',
    'Assam': 'AS',
    'Bihar': 'BR',
    'Chandigarh': 'CH',
    'Chhattisgarh': 'CT',
    'Dadra and Nagar Haveli and Daman and Diu': 'DN',
    'Delhi': 'DL',
    'Goa': 'GA',
    'Gujarat': 'GJ',
    'Haryana': 'HR',
    'Himachal Pradesh': 'HP',
    'Jammu & Kashmir': 'JK',
    'Jharkhand': 'JH',
    'Karnataka': 'KA',
    'Kerala': 'KL',
    'Ladakh': 'LA',
    'Lakshadweep': 'LD',
    'Madhya Pradesh': 'MP',
    'Maharashtra': 'MH',
    'Manipur': 'MN',
    'Meghalaya': 'ML',
    'Mizoram': 'MZ',
    'Nagaland': 'NL',
    'Odisha': 'OR',
    'Puducherry': 'PY',
    'Punjab': 'PB',
    'Rajasthan': 'RJ',
    'Sikkim': 'SK',
    'Tamil Nadu': 'TN',
    'Telangana': 'TG',
    'Tripura': 'TR',
    'Uttar Pradesh': 'UP',
    'Uttarakhand': 'UT',
    'West Bengal': 'WB'
}

def normalize_state_name(state_name):
    """Convert database state name to display name"""
    return STATE_NAME_MAPPING.get(state_name.lower(), state_name.title())

def create_india_choropleth(df, value_column, title, color_scale='Purples'):
    """
    Create an interactive choropleth map of India
    
    Parameters:
    - df: DataFrame with 'state' column and value column
    - value_column: Column name containing the metric to visualize
    - title: Chart title
    - color_scale: Plotly color scale (default: Purples for PhonePe branding)
    """
    # Normalize state names
    df['state_display'] = df['state'].apply(normalize_state_name)
    df['state_code'] = df['state_display'].map(STATE_ISO_MAPPING)
    
    # Create hover text with formatted values
    if 'amount' in value_column.lower():
        df['hover_text'] = df.apply(
            lambda row: f"<b>{row['state_display']}</b><br>" +
                       f"Amount: ₹{row[value_column]:,.0f}<br>" +
                       (f"Transactions: {row.get('total_transactions', 0):,.0f}" 
                        if 'total_transactions' in df.columns else ""),
            axis=1
        )
    else:
        df['hover_text'] = df.apply(
            lambda row: f"<b>{row['state_display']}</b><br>" +
                       f"Transactions: {row[value_column]:,.0f}",
            axis=1
        )
    
    # Create choropleth using India geojson
    fig = go.Figure()
    
    # Add choropleth trace
    fig.add_trace(go.Choropleth(
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations=df['state_display'],
        z=df[value_column],
        colorscale=color_scale,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar=dict(
            title=value_column.replace('_', ' ').title(),
            thickness=15,
            len=0.7,
            bgcolor='rgba(26,26,26,0.8)',
            tickfont=dict(color='white'),
            titlefont=dict(color='white'),
            x=0.95
        ),
        hovertemplate='%{text}<extra></extra>',
        text=df['hover_text']
    ))
    
    # Update layout
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        showcountries=False,
        showcoastlines=False,
        showland=False,
        showocean=False,
        bgcolor='#1a1a1a'
    )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='white')
        ),
        geo=dict(
            scope='asia',
            projection=dict(type='mercator'),
            center=dict(lat=22, lon=79),
            lonaxis=dict(range=[68, 98]),
            lataxis=dict(range=[6, 38]),
            bgcolor='#1a1a1a'
        ),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#1a1a1a',
        font=dict(family="Arial, sans-serif", size=12, color='white')
    )
    
    return fig

def create_state_detail_card(state_data):
    """Create a detailed information card for selected state"""
    return f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; margin: 10px 0;">
        <h3 style="margin: 0 0 15px 0; color: white;">{state_data.get('state', 'N/A')}</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">Total Transactions</p>
                <h2 style="margin: 0; color: white;">{state_data.get('transactions_formatted', '0')}</h2>
            </div>
            <div>
                <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">Total Amount</p>
                <h2 style="margin: 0; color: white;">₹{state_data.get('amount_formatted', '0')}</h2>
            </div>
        </div>
    </div>
    """

def format_large_number(num):
    """Format large numbers with appropriate suffix"""
    if num >= 1e12:
        return f"{num/1e12:.2f}T"
    elif num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif num >= 1e3:
        return f"{num/1e3:.2f}K"
    else:
        return f"{num:.0f}"

def get_district_data(conn, state, year_condition=""):
    """
    Get district-level data for a specific state
    
    Parameters:
    - conn: Database connection
    - state: State name
    - year_condition: SQL year filter condition
    
    Returns:
    - DataFrame with district-level data
    """
    query = f"""
    SELECT 
        district,
        SUM(transaction_count) as total_transactions,
        ROUND(SUM(transaction_amount) / 1e9, 2) as amount_billions
    FROM map_transaction
    WHERE state = '{state}' {year_condition}
    GROUP BY district
    ORDER BY total_transactions DESC
    LIMIT 20
    """
    
    try:
        import sqlite3
        import pandas as pd
        df = pd.read_sql_query(query, conn)
        return df
    except:
        return None

def create_district_bar_chart(df, state_name, metric='total_transactions'):
    """Create a bar chart for district-level data"""
    if df is None or df.empty:
        return None
    
    title = f"Top Districts in {normalize_state_name(state_name)}"
    
    if metric == 'total_transactions':
        fig = px.bar(
            df,
            x='district',
            y='total_transactions',
            title=title + " - Transaction Volume",
            labels={'total_transactions': 'Transactions', 'district': 'District'},
            color='total_transactions',
            color_continuous_scale='Purples'
        )
    else:
        fig = px.bar(
            df,
            x='district',
            y='amount_billions',
            title=title + " - Transaction Amount (Billions ₹)",
            labels={'amount_billions': 'Amount (Billions)', 'district': 'District'},
            color='amount_billions',
            color_continuous_scale='Blues'
        )
    
    fig.update_layout(
        xaxis={'tickangle': 45, 'color': 'white', 'gridcolor': '#333333'},
        yaxis={'color': 'white', 'gridcolor': '#333333'},
        showlegend=False,
        height=400,
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        title_font=dict(color='white')
    )
    
    return fig
