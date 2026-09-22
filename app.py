import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Team Performance Dashboard", layout="wide")
st.title("👥 Supervisor & Manager Performance Leaderboard")
st.markdown("Use this interactive platform to analyze performance trends across your supervisors and branch managers.")

# 2. Advanced Data Loading Helper
@st.cache_data
def load_data():
    # Load corporate CSV file and skip the file title row
    df = pd.read_csv("sales_data.csv", skiprows=1)
    
    # Clean whitespace out of row headers
    df.columns = [str(col).strip() for col in df.columns]
    
    # Purge summary total row from the dataset if present
    if 'S. No.' in df.columns:
        df = df[df['S. No.'].astype(str).str.lower() != 'total']
        df = df[df['StoreName'].dropna().str.lower() != 'total']
        
    # Standardize data values to float numerical types
    df['MTD NetSale'] = pd.to_numeric(df['MTD NetSale'], errors='coerce')
    df['PL Pharma NetSale'] = pd.to_numeric(df['PL Pharma NetSale'], errors='coerce')
    df['PL NonPharma NetSale'] = pd.to_numeric(df['PL NonPharma NetSale'], errors='coerce')
    
    return df

try:
    df = load_data()
    
    # 3. Sidebar Filtering Systems
    st.sidebar.header("🎯 Personnel Breakdown Options")
    
    # Supervisor filtering array
    supervisors = ["All Supervisors"] + sorted(list(df["RSS Manager"].dropna().unique()))
    selected_super = st.sidebar.selectbox("Filter by RSS Supervisor", supervisors)
    
    # Manager filtering array
    managers = ["All Managers"] + sorted(list(df["Manager"].dropna().unique()))
    selected_manager = st.sidebar.selectbox("Filter by Store Manager", managers)
    
    # Apply filtering sequence
    filtered_df = df.copy()
    if selected_super != "All Supervisors":
        filtered_df = filtered_df[filtered_df["RSS Manager"] == selected_super]
    if selected_manager != "All Managers":
        filtered_df = filtered_df[filtered_df["Manager"] == selected_manager]

    # 4. Global Sales Performance Scorecards
    total_revenue = filtered_df["MTD NetSale"].sum()
    pharma_total = filtered_df["PL Pharma NetSale"].sum()
    non_pharma_total = filtered_df["PL NonPharma NetSale"].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Selected Group Net Revenue", value=f"₹{total_revenue:,.2f}")
    with col2:
        st.metric(label="💊 Pharma Sales (PL)", value=f"₹{pharma_total:,.2f}")
    with col3:
        st.metric(label="🛍️ Non-Pharma Sales (PL)", value=f"₹{non_pharma_total:,.2f}")

    st.markdown("---")

    # 5. Visualizations Section (Two Columns)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📊 Performance by RSS Supervisor")
        # Aggregate data by RSS Manager
        super_perf = df.groupby("RSS Manager")["MTD NetSale"].sum().reset_index()
        fig_super = px.bar(
            super_perf,
            x="MTD NetSale",
            y="RSS Manager",
            orientation="h",
            color="MTD NetSale",
            color_continuous_scale="Blues",
            labels={"MTD NetSale": "Total Net Sales (₹)", "RSS Manager": "Supervisor Name"}
        )
        fig_super.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_super, use_container_width=True)

    with chart_col2:
        st.subheader("📊 Top 10 Managers Performance")
        # Aggregate data by Local Store Manager
        manager_perf = filtered_df.groupby("Manager")["MTD NetSale"].sum().reset_index()
        top_10_managers = manager_perf.nlargest(10, "MTD NetSale")
        
        fig_mgr = px.bar(
            top_10_managers,
            x="MTD NetSale",
            y="Manager",
            orientation="h",
            color="MTD NetSale",
            color_continuous_scale="Teal",
            labels={"MTD NetSale": "Total Net Sales (₹)", "Manager": "Manager Name"}
        )
        fig_mgr.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_mgr, use_container_width=True)

    st.markdown("---")

    # 6. Comprehensive Corporate Spreadsheet Grid View
    st.subheader("📋 Team Ranking & Performance Metrics Grid")
    display_cols = ["StoreName", "RSS Manager", "Manager", "Format", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale"]
    
    # Sort entire table by highest producing entities first
    final_table = filtered_df[display_cols].dropna(subset=["StoreName"]).sort_values(by="MTD NetSale", ascending=False)
    st.dataframe(final_table, use_container_width=True)

except Exception as e:
    st.error(f"Configuration adjustment required: {e}")
