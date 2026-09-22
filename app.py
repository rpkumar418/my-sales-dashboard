import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page & Layout Setup
st.set_page_config(page_title="Team Performance Dashboard", layout="wide")
st.title("👥 Supervisor & Manager Performance Leaderboard")
st.markdown("Track and evaluate MTD performance metrics across senior supervisors and store managers.")

# 2. Advanced Data Loading and Cleaning Engine
@st.cache_data
def load_data():
    try:
        # Step A: Read the raw lines of the file first to find the true header row
        with open("sales_data.csv", "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # Find which line actually contains the column headers
        header_idx = 0
        for i, line in enumerate(lines):
            if "StoreName" in line or "StoreID" in line:
                header_idx = i
                break
        
        # Step B: Read the CSV using the correct header row dynamic index
        df = pd.read_csv("sales_data.csv", skiprows=header_idx)
        
        # Step C: Standardise columns by removing trailing or hidden spaces
        df.columns = [str(col).strip() for col in df.columns]
        
        # Step D: Remove any summary "Total" or empty rows at the bottom
        if 'S. No.' in df.columns:
            df = df[df['S. No.'].astype(str).str.lower().str.strip() != 'total']
        if 'StoreName' in df.columns:
            df = df[df['StoreName'].dropna().str.lower().str.strip() != 'total']
            
        # Step E: Enforce strict clean numeric types on performance metric values
        df['MTD NetSale'] = pd.to_numeric(df['MTD NetSale'], errors='coerce').fillna(0)
        df['PL Pharma NetSale'] = pd.to_numeric(df['PL Pharma NetSale'], errors='coerce').fillna(0)
        df['PL NonPharma NetSale'] = pd.to_numeric(df['PL NonPharma NetSale'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error reading file structure: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ The app loaded but the data file could not be parsed yet. Please check your GitHub repository layout.")
else:
    # 3. Sidebar Filtering Systems
    st.sidebar.header("🎯 Personnel Breakdown Options")
    
    # Extract unique senior supervisor names cleanly
    super_list = ["All Supervisors"] + sorted([str(x).strip() for x in df["RSS Manager"].dropna().unique() if str(x).strip() != ""])
    selected_super = st.sidebar.selectbox("Filter by RSS Supervisor", super_list)
    
    # Extract unique store manager names cleanly
    mgr_list = ["All Managers"] + sorted([str(x).strip() for x in df["Manager"].dropna().unique() if str(x).strip() != ""])
    selected_manager = st.sidebar.selectbox("Filter by Store Manager", mgr_list)
    
    # Cascade filters down across the dataset
    filtered_df = df.copy()
    if selected_super != "All Supervisors":
        filtered_df = filtered_df[filtered_df["RSS Manager"].str.strip() == selected_super]
    if selected_manager != "All Managers":
        filtered_df = filtered_df[filtered_df["Manager"].str.strip() == selected_manager]

    # 4. Interactive Performance Cards
    total_net = filtered_df["MTD NetSale"].sum()
    total_pharma = filtered_df["PL Pharma NetSale"].sum()
    total_non_pharma = filtered_df["PL NonPharma NetSale"].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Selected Performance Net Revenue", value=f"₹{total_net:,.2f}")
    with col2:
        st.metric(label="💊 Private Label Pharma Sales", value=f"₹{total_pharma:,.2f}")
    with col3:
        st.metric(label="🛍️ Private Label Non-Pharma Sales", value=f"₹{total_non_pharma:,.2f}")

    st.markdown("---")

    # 5. Side-by-Side Analytical Visualization Panels
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📊 Performance by RSS Supervisor")
        super_perf = df.groupby("RSS Manager")["MTD NetSale"].sum().reset_index()
        super_perf = super_perf.sort_values(by="MTD NetSale", ascending=True)
        
        fig_super = px.bar(
            super_perf,
            x="MTD NetSale",
            y="RSS Manager",
            orientation="h",
            color="MTD NetSale",
            color_continuous_scale="Blues",
            labels={"MTD NetSale": "Total Sales (₹)", "RSS Manager": "Supervisor"}
        )
        fig_super.update_layout(showlegend=False)
        st.plotly_chart(fig_super, use_container_width=True)

    with chart_col2:
        st.subheader("📊 Top 10 Managers Performance Leaderboard")
        manager_perf = filtered_df.groupby("Manager")["MTD NetSale"].sum().reset_index()
        top_10_mgr = manager_perf.nlargest(10, "MTD NetSale").sort_values(by="MTD NetSale", ascending=True)
        
        fig_mgr = px.bar(
            top_10_mgr,
            x="MTD NetSale",
            y="Manager",
            orientation="h",
            color="MTD NetSale",
            color_continuous_scale="Teal",
            labels={"MTD NetSale": "Total Sales (₹)", "Manager": "Manager Name"}
        )
        fig_mgr.update_layout(showlegend=False)
        st.plotly_chart(fig_mgr, use_container_width=True)

    st.markdown("---")

    # 6. Deep-Dive Performance Spreadsheet Grid View
    st.subheader("📋 Team Ranking & Performance Metrics Grid")
    display_cols = ["StoreName", "RSS Manager", "Manager", "Format", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale"]
    
    # Present a beautifully structured performance ranking order table
    final_table = filtered_df[display_cols].sort_values(by="MTD NetSale", ascending=False)
    st.dataframe(final_table, use_container_width=True)
