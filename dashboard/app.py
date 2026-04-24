"""
Tesla Market Tracker - Standalone Dashboard
Works with sample data, no database required
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
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

# Hide Streamlit branding
hide_streamlit_style = """
    <style>
        .stAppDeployButton { display: none !important; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Title
st.title("🚗 Tesla Used Inventory & Cross-Brand Market Tracker")
st.markdown("*Real-time used car market intelligence*")
st.markdown("---")

# Sample data (realistic market data)
@st.cache_data
def get_data():
    return pd.DataFrame({
        'brand': [
            'Tesla', 'Tesla', 'Tesla', 'Tesla', 'Tesla',
            'Ford', 'Ford', 'Ford', 'Ford',
            'BMW', 'BMW', 'BMW',
            'Hyundai', 'Hyundai',
            'Kia', 'Kia',
            'Toyota', 'Toyota',
            'Mercedes', 'Mercedes',
            'Volkswagen', 'Polestar'
        ],
        'model': [
            'Model 3', 'Model 3', 'Model Y', 'Model Y', 'Model S',
            'Mustang Mach-E', 'Mustang Mach-E', 'F-150 Lightning', 'F-150 Lightning',
            'i4', 'i4', 'iX',
            'Ioniq 5', 'Ioniq 5',
            'EV6', 'EV6',
            'Prius', 'bZ4X',
            'EQS', 'EQE',
            'ID.4', 'Polestar 2'
        ],
        'year': [2022, 2023, 2022, 2023, 2021, 2022, 2023, 2023, 2022, 2022, 2023, 2023, 2022, 2023, 2022, 2023, 2022, 2023, 2022, 2023, 2023, 2022],
        'price': [42990, 45990, 49990, 54990, 69990, 42990, 48990, 65990, 58990, 49990, 52990, 79990, 38990, 42990, 37990, 42990, 28990, 35990, 89990, 69990, 35990, 39990],
        'mileage': [15234, 8234, 12345, 5678, 25678, 18345, 9876, 5678, 12345, 12345, 5678, 4567, 18345, 9876, 15678, 8765, 23456, 12345, 12345, 5678, 12000, 21567],
        'location_state': ['CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA', 'CA']
    })

df = get_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

brands = st.sidebar.multiselect(
    "Select Brands",
    options=sorted(df['brand'].unique()),
    default=['Tesla', 'Ford', 'BMW']
)

years = st.sidebar.slider(
    "Model Year Range",
    min_value=2021,
    max_value=2023,
    value=(2021, 2023)
)

price_range = st.sidebar.slider(
    "Price Range ($)",
    min_value=25000,
    max_value=90000,
    value=(25000, 70000)
)

# Apply filters
filtered_df = df[
    (df['brand'].isin(brands)) &
    (df['year'].between(years[0], years[1])) &
    (df['price'].between(price_range[0], price_range[1]))
]

# Metrics
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

# Chart 1: Price by Brand
if not filtered_df.empty:
    st.subheader("📊 Average Price by Brand")
    price_by_brand = filtered_df.groupby('brand')['price'].mean().reset_index()
    fig = px.bar(price_by_brand, x='brand', y='price', color='brand',
                  title="Average Price by Brand", labels={'price': 'Avg Price ($)'})
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Price vs Mileage
st.subheader("📈 Price vs Mileage")
if not filtered_df.empty:
    fig = px.scatter(filtered_df, x='mileage', y='price', color='brand',
                     hover_data=['model', 'year'], title="Price vs Mileage")
    st.plotly_chart(fig, use_container_width=True)

# Chart 3: Depreciation
st.subheader("📉 Depreciation by Year")
if not filtered_df.empty:
    price_by_year = filtered_df.groupby(['brand', 'year'])['price'].mean().reset_index()
    fig = px.line(price_by_year, x='year', y='price', color='brand', markers=True,
                  title="Average Price by Year (Depreciation Curve)")
    st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("📋 Listings")
st.dataframe(filtered_df[['brand', 'model', 'year', 'price', 'mileage', 'location_state']], use_container_width=True)

# Export
csv = filtered_df.to_csv(index=False)
st.download_button("📥 Download CSV", csv, "used_car_listings.csv", "text/csv")

st.caption("Data sample | Tesla Market Tracker")