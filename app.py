import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Store Sales Dashboard", layout="wide")
st.title("📊 Store Sales Interactive Dashboard")
st.markdown("Welcome! This app helps you easily track and demonstrate our store performance.")

# 2. Advanced Data Loading Helper
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    # Clean up column names by stripping hidden spaces and converting to string
    df.columns = [str(col).strip() for col in df.columns]
    
    # Auto-convert Date column to readable timeline dates if it exists
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values('Date')
    return df

try:
    df = load_data()
    
    # Double-check that our required columns are present
    required_cols = ['Date', 'Product', 'Quantity', 'Unit_Price', 'Total_Sales']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"⚠️ Almost there! The app is looking for these missing columns: {missing_cols}")
        st.info(f"🔍 Currently, your spreadsheet only contains these columns: **{list(df.columns)}**")
        st.warning("Please edit your CSV file row headers to match exactly, or let your teacher know what columns it found!")
    else:
        # 3. Create a sidebar filter for the products
        st.sidebar.header("Filter Options")
        all_products = ["All Products"] + sorted(list(df["Product"].dropna().unique()))
        selected_product = st.sidebar.selectbox("Choose a Product to Inspect", all_products)
        
        # Filter data based on selection
        if selected_product != "All Products":
            filtered_df = df[df["Product"] == selected_product]
        else:
            filtered_df = df

        # 4. Display Key Scorecards
        total_revenue = pd.to_numeric(filtered_df["Total_Sales"], errors='coerce').sum()
        total_units = pd.to_numeric(filtered_df["Quantity"], errors='coerce').sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💰 Total Sales Revenue", value=f"${total_revenue:,.2f}")
        with col2:
            st.metric(label="📦 Total Units Sold", value=f"{total_units:,}")

        # 5. Build an interactive timeline chart
        st.subheader("📈 Sales Over Time")
        fig = px.line(
            filtered_df, 
            x="Date", 
            y="Total_Sales", 
            color="Product", 
            title="Sales Progress Timeline",
            labels={"Total_Sales": "Revenue ($)", "Date": "Timeline"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # 6. Show the raw table below
        st.subheader("📋 Detailed Data View")
        st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Something unexpected happened while opening the file: {e}")
