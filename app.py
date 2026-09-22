import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Set up the page title
st.set_page_config(page_title="Store Sales Dashboard", layout="wide")
st.title("📊 Store Sales Interactive Dashboard")
st.markdown("Welcome! This app helps you easily track and demonstrate our store performance.")

# 2. Load the spreadsheet data
@st.cache_data
def load_data():
    # Looks for your file in the same folder
    df = pd.read_csv("sales_data.csv")
    return df

try:
    df = load_data()
    
    # 3. Create a sidebar filter for the products
    st.sidebar.header("Filter Options")
    all_products = ["All"] + list(df["Product"].unique())
    selected_product = st.sidebar.selectbox("Choose a Product to Inspect", all_products)
    
    # Filter data based on selection
    if selected_product != "All":
        filtered_df = df[df["Product"] == selected_product]
    else:
        filtered_df = df

    # 4. Display Key Scorecards
    total_revenue = filtered_df["Total_Sales"].sum()
    total_units = filtered_df["Quantity"].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="💰 Total Sales Revenue", value=f"${total_revenue:,.2f}")
    with col2:
        st.metric(label="📦 Total Units Sold", value=f"{total_units:,}")

    # 5. Build an interactive chart
    st.subheader("📈 Sales Over Time")
    fig = px.line(filtered_df, x="Date", y="Total_Sales", color="Product", title="Sales Progress Timeline")
    st.plotly_chart(fig, use_container_width=True)

    # 6. Show the raw table below
    st.subheader("📋 Detailed Data View")
    st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error("Let's configure your spreadsheet! Ensure your columns match: 'Date', 'Product', 'Quantity', 'Unit_Price', and 'Total_Sales'.")
