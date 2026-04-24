"""
Streamlit Dashboard for Tesla Market Tracker - Clean Version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_engine

# ============================================
# PAGE CONFIGURATION - REMOVE DEPLOYMENT OPTIONS
# ============================================
st.set_page_config(
    page_title="Tesla Market Tracker",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ============================================
# HIDE STREAMLIT DEPLOYMENT UI ELEMENTS
# ============================================
hide_streamlit_style = """
    <style>
        /* Hide the deploy button */
        .stAppDeployButton {
            display: none !important;
        }
        
        /* Hide the main menu */
        #MainMenu {
            visibility: hidden;
        }
        
        /* Hide footer */
        footer {
            visibility: hidden;
        }
        
        /* Hide header */
        header {
            visibility: hidden;
        }
        
        /* Hide "Made with Streamlit" */
        .st-emotion-cache-1dj5sot {
            display: none !important;
        }
        
        /* Hide any deployment-related buttons */
        button[data-testid="baseButton-header"] {
            display: none !important;
        }
        
        /* Hide the manage app button */
        .st-emotion-cache-1r6slb0 {
            display: none !important;
        }
        
        /* Reduce top padding since header is hidden */
        .main > div {
            padding-top: 1rem;
        }
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ============================================
# TITLE AND HEADER
# ============================================
st.title("🚗 Tesla Used Inventory & Cross-Brand Market Tracker")
st.markdown("*Real-time used car market intelligence*")
st.markdown("---")

# ============================================
# LOAD DATA
# ============================================
@st.cache_data(ttl=3600)
def load_data():
    """Load listings from database"""
    engine = get_engine()
    try:
        query = "SELECT * FROM listings ORDER BY scraped_at DESC"
        df = pd.read_sql(query, engine)
        return df
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.info("📭 No data available yet. Run the scraper first.")
    st.stop()

# ============================================
# SIDEBAR FILTERS
# ============================================
st.sidebar.header("🔍 Filters")

# Brand selector
brands = st.sidebar.multiselect(
    "Select Brands",
    options=sorted(df['brand'].unique()),
    default=['Tesla']
)

# Year range
min_year = int(df['year'].min()) if not df.empty else 2020
max_year = int(df['year'].max()) if not df.empty else 2025
years = st.sidebar.slider(
    "Model Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Price range
min_price = int(df['price'].min()) if not df.empty else 0
max_price = int(df['price'].max()) if not df.empty else 100000
price_range = st.sidebar.slider(
    "Price Range ($)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# ============================================
# APPLY FILTERS
# ============================================
filtered_df = df[
    (df['brand'].isin(brands)) &
    (df['year'].between(years[0], years[1])) &
    (df['price'].between(price_range[0], price_range[1]))
]

# ============================================
# METRICS ROW
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Listings", len(filtered_df))

with col2:
    avg_price = filtered_df['price'].mean() if not filtered_df.empty else 0
    st.metric("💰 Average Price", f"${avg_price:,.0f}")

with col3:
    avg_mileage = filtered_df['mileage'].mean() if not filtered_df.empty else 0
    st.metric("📏 Average Mileage", f"{avg_mileage:,.0f}")

with col4:
    unique_models = filtered_df['model'].nunique() if not filtered_df.empty else 0
    st.metric("🚙 Unique Models", unique_models)

st.markdown("---")

# ============================================
# CHART 1: Price by Brand and Model
# ============================================
st.subheader("📊 Average Price by Brand & Model")

if not filtered_df.empty:
    price_by_model = filtered_df.groupby(['brand', 'model'])['price'].mean().reset_index()
    fig = px.bar(
        price_by_model,
        x='model',
        y='price',
        color='brand',
        title="Average Price Comparison",
        labels={'price': 'Average Price ($)', 'model': 'Model'},
        text_auto='.0s'
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for selected filters")

# ============================================
# CHART 2: Price vs Mileage
# ============================================
st.subheader("📈 Price vs Mileage Analysis")

if not filtered_df.empty:
    fig = px.scatter(
        filtered_df,
        x='mileage',
        y='price',
        color='brand',
        hover_data=['model', 'year', 'location_state'],
        title="Price vs Mileage Scatter Plot",
        labels={'mileage': 'Mileage', 'price': 'Price ($)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# CHART 3: Depreciation Analysis
# ============================================
st.subheader("📉 Depreciation Analysis")

if not filtered_df.empty:
    price_by_year = filtered_df.groupby(['brand', 'year'])['price'].mean().reset_index()
    fig = px.line(
        price_by_year,
        x='year',
        y='price',
        color='brand',
        title="Average Price by Model Year (Depreciation Curve)",
        labels={'year': 'Model Year', 'price': 'Average Price ($)'},
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# CHART 4: Geographic Distribution
# ============================================
st.subheader("🗺️ Geographic Price Distribution")

if not filtered_df.empty and filtered_df['location_state'].notna().any():
    geo_data = filtered_df[filtered_df['location_state'] != ''].groupby('location_state').agg({
        'price': 'mean',
        'id': 'count'
    }).reset_index()
    geo_data.columns = ['state', 'avg_price', 'count']
    
    fig = px.choropleth(
        geo_data,
        locations='state',
        locationmode="USA-states",
        color='avg_price',
        hover_name='state',
        scope="usa",
        title="Average Price by State",
        labels={'avg_price': 'Average Price ($)'},
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# DATA TABLE
# ============================================
st.subheader("📋 Recent Listings")

if not filtered_df.empty:
    display_cols = ['brand', 'model', 'year', 'price', 'mileage', 'location_state', 'scraped_at']
    available_cols = [col for col in display_cols if col in filtered_df.columns]
    display_df = filtered_df[available_cols].head(100)
    st.dataframe(display_df, use_container_width=True)

# ============================================
# EXPORT BUTTON
# ============================================
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Data as CSV",
    data=csv,
    file_name="used_car_listings.csv",
    mime="text/csv"
)

# ============================================
# FOOTER - CLEAN (NO DEPLOYMENT MESSAGES)
# ============================================
st.markdown("---")
st.caption("Data updated daily | Source: Multiple automotive inventory APIs")