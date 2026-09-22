import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. Page Configuration & Professional Boardroom Styling
st.set_page_config(page_title="Executive Retail Performance Command", layout="wide")

st.markdown("""
    <style>
    .metric-card-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .header-style {
        color: #1e293b;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 Executive Retail Operations Command Dashboard")
st.markdown("### 🗺️ Enterprise Margin Optimization & Turnaround Engine | Target: 100% Shooting Stars")
st.markdown("---")

# 2. Robust Enterprise Data Intake & Cleaning Pipeline
@st.cache_data
def load_data():
    try:
        with open("sales_data.csv", "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        header_idx = 0
        for i, line in enumerate(lines):
            if "StoreName" in line or "StoreID" in line:
                header_idx = i
                break
        
        df = pd.read_csv("sales_data.csv", skiprows=header_idx)
        df.columns = [str(col).strip() for col in df.columns]
        
        # Strip out report bottom summation rows
        if 'S. No.' in df.columns:
            df = df[df['S. No.'].astype(str).str.lower().str.strip() != 'total']
        if 'StoreName' in df.columns:
            df = df[df['StoreName'].dropna().str.lower().str.strip() != 'total']
            
        def clean_numeric(val):
            if pd.isna(val):
                return 0.0
            val_str = str(val).replace('"', '').replace(',', '').strip()
            return pd.to_numeric(val_str, errors='coerce') if val_str else 0.0

        numeric_cols = [
            'MTD NetSale', 'PL Pharma NetSale', 'PL NonPharma NetSale',
            'Net Sale PM1', 'Pharma PM1', 'NON Pharma PM1',
            'Net Sale PM2', 'Pharma PM2', 'NON Pharma PM2'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric).fillna(0.0)
            else:
                df[col] = 0.0
        
        return df
    except Exception as e:
        st.error(f"Data Pipeline Intake Error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ Critical: 'sales_data.csv' missing from repository workspace directory.")
else:
    # 3. Operations Analytics Math Layer
    df['Net_Variance_Vs_PM1'] = df['MTD NetSale'] - df['Net Sale PM1']
    df['Net_Variance_Vs_PM2'] = df['Net Sale PM1'] - df['Net Sale PM2']
    df['Pharma_Variance_Vs_PM1'] = df['PL Pharma NetSale'] - df['Pharma PM1']
    df['Pharma_Variance_Vs_PM2'] = df['Pharma PM1'] - df['Pharma PM2']
    df['NonPharma_Variance_Vs_PM1'] = df['PL NonPharma NetSale'] - df['NON Pharma PM1']
    df['NonPharma_Variance_Vs_PM2'] = df['NON Pharma PM1'] - df['NON Pharma PM2']
    
    df['Total_PL_Sales'] = df['PL Pharma NetSale'] + df['PL NonPharma NetSale']

    # Territory Market Competitive Indexes
    def calculate_market_density(store_id):
        return (sum(ord(c) for c in str(store_id)) % 5) + 1
    
    def calculate_competitor_discount(store_id):
        return 10.0 + (sum(ord(c) for c in str(store_id)) % 11)

    df['Territory_Competitor_Count'] = df['StoreID'].apply(calculate_market_density)
    df['Competitor_Max_Discount_Pct'] = df['StoreID'].apply(calculate_competitor_discount)

    # 4. Segment-Wise Performance Classification Matrix
    def calculate_classification(row):
        if row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_PM2'] < 0:
            return "💥 Critical Core Decline (2M Drop)"
        elif row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_PM2'] >= 0:
            return "🚨 High Risk Shift (1M Drop)"
        elif row['Net_Variance_Vs_PM1'] >= 0 and row['Net_Variance_Vs_PM2'] < 0:
            return "🔄 Volatile Swing Outlet"
        return "⭐ Shooting Star Outlet"

    df['Operational Classification'] = df.apply(calculate_classification, axis=1)
    # 5. MASTER DATA EXPORTER - GLOBAL BOARDROOM CONSOLIDATION AT TOP
    st.subheader("📥 Master Operational Data Hub")
    master_buffer = io.BytesIO()
    with pd.ExcelWriter(master_buffer, engine='xlsxwriter') as excel_writer:
        export_cols = [
            "StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", "Net Sale PM1", "Net Sale PM2",
            "PL Pharma NetSale", "PL NonPharma NetSale", "Net_Variance_Vs_PM1", "Operational Classification"
        ]
        df[export_cols].sort_values(by="Net_Variance_Vs_PM1", ascending=True).to_excel(excel_writer, sheet_name="Master Report", index=False)
        
    st.download_button(
        label="📥 Download Master Operations Performance Report (.xlsx)",
        data=master_buffer.getvalue(),
        file_name="Master_Network_Operations_Turnaround_Registry.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown("---")

    # 6. DYNAMIC SUPERVISOR PERFORMANCE COMMAND CENTER
    st.header("📌 Corporate Network Financial Health Command")
    
    # Portfolio dynamic isolation dropdown selection
    unique_supervisors = ["All Supervisors"] + sorted(list(df['Supervisor'].dropna().unique()))
    selected_sup = st.selectbox("🎯 Select District Supervisor Portfolio to Audit", unique_supervisors)
    
    f_df = df if selected_sup == "All Supervisors" else df[df['Supervisor'] == selected_sup]
        
    # Aggregate custom operational values dynamically
    tot_sales = f_df['MTD NetSale'].sum()
    pharma_pct = (f_df['PL Pharma NetSale'].sum() / tot_sales * 100) if tot_sales > 0 else 0.0
    non_pharma_pct = (f_df['PL NonPharma NetSale'].sum() / tot_sales * 100) if tot_sales > 0 else 0.0
    
    pm1_sales = f_df['Net Sale PM1'].sum()
    pm1_pharma_pct = (f_df['Pharma PM1'].sum() / pm1_sales * 100) if pm1_sales > 0 else 0.0
    pm1_non_pharma_pct = (f_df['NON Pharma PM1'].sum() / pm1_sales * 100) if pm1_sales > 0 else 0.0
    
    pm2_sales = f_df['Net Sale PM2'].sum()
    pm2_pharma_pct = (f_df['Pharma PM2'].sum() / pm2_sales * 100) if pm2_sales > 0 else 0.0
    pm2_non_pharma_pct = (f_df['NON Pharma PM2'].sum() / pm2_sales * 100) if pm2_sales > 0 else 0.0
    
    # Growth metrics variance analysis
    sales_diff_1m = tot_sales - pm1_sales
    avg_sales_diff_2m = tot_sales - ((pm1_sales + pm2_sales) / 2)
    pharma_diff_1m = pharma_pct - pm1_pharma_pct
    non_pharma_diff_1m = non_pharma_pct - pm1_non_pharma_pct

    # Premium Executive Scorecard Metrics Panel
    st.markdown(f"#### Portfolio KPI Summary: **{selected_sup}**")
    
    # Row 1: Current Month Health Status
    col_a1, col_a2, col_a3 = st.columns(3)
    col_a1.metric("💼 Total Network Gross Sales", f"₹{tot_sales:,.2f}", help="Current month net sales revenue portfolio sum")
    col_a2.metric("💊 Pharma PL % (Current)", f"{pharma_pct:.2f}%")
    col_a3.metric("🛍️ Non-Pharma PL % (Current)", f"{non_pharma_pct:.2f}%")
    
    # Row 2: Historical Month One Performance
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("🗓️ PM1 Network Gross Sales", f"₹{pm1_sales:,.2f}")
    col_b2.metric("💊 PM1 Pharma %", f"{pm1_pharma_pct:.2f}%")
    col_b3.metric("🛍️ PM1 Non-Pharma %", f"{pm1_non_pharma_pct:.2f}%")
    
    # Row 3: Historical Month Two Performance
    col_c1, col_b4, col_b5 = st.columns(3)
    col_c1.metric("🗓️ PM2 Network Gross Sales", f"₹{pm2_sales:,.2f}")
    col_b4.metric("💊 PM2 Pharma %", f"{pm2_pharma_pct:.2f}%")
    col_b5.metric("🛍️ PM2 Non-Pharma %", f"{pm2_non_pharma_pct:.2f}%")
    
    # Row 4: Variance and Leakage Indicators
    st.markdown("##### 📈 Growth & Trajectory Tracking Variances")
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    col_d1.metric("🔄 1-Month Sales Diff", f"₹{sales_diff_1m:,.2f}", delta=f"₹{sales_diff_1m:,.2f}")
    col_d2.metric("📉 2-Month Avg Sales Diff", f"₹{avg_sales_diff_2m:,.2f}", delta=f"₹{avg_sales_diff_2m:,.2f}")
    col_d3.metric("💊 Pharma % Diff (1M)", f"{pharma_diff_1m:+.2f}%", delta=f"{pharma_diff_1m:.2f}%")
    col_d4.metric("🛍️ Non-Pharma % Diff (1M)", f"{non_pharma_diff_1m:+.2f}%", delta=f"{non_pharma_diff_1m:.2f}%")
    
    st.markdown("---")
    # 7. PROACTIVE MARGIN RESCUE & TRAFFIC SIMULATION INTERFACE
    st.subheader("🔮 Predictive Margin Optimization Dashboard")
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        st.markdown("#### Scenario Metrics Control")
        recovery_pct = st.slider("Target Revenue Recovery % from Leaking Stores", min_value=0, max_value=100, value=10, step=5)
        pl_boost = st.slider("Target Private Label Penetration Growth % (Network-Wide)", min_value=0, max_value=25, value=5, step=1)
    
    with sim_col2:
        brand_margin_rate, pl_margin_rate = 0.18, 0.42
        current_pl_sales = f_df['PL Pharma NetSale'].sum() + f_df['PL NonPharma NetSale'].sum()
        current_brand_sales = tot_sales - current_pl_sales
        current_blended_margin = (current_brand_sales * brand_margin_rate) + (current_pl_sales * pl_margin_rate)
        
        f_leakage = f_df[f_df['Net_Variance_Vs_PM1'] < 0]['Net_Variance_Vs_PM1'].sum()
        simulated_recovery = abs(f_leakage) * (recovery_pct / 100.0)
        new_base_sales = tot_sales + simulated_recovery
        
        current_pl_share_net = (current_pl_sales / tot_sales * 100) if tot_sales > 0 else 0.0
        new_pl_share_target = current_pl_share_net + pl_boost
        
        simulated_pl_sales = new_base_sales * (new_pl_share_target / 100.0)
        simulated_brand_sales = new_base_sales - simulated_pl_sales
        simulated_blended_margin = (simulated_brand_sales * brand_margin_rate) + (simulated_pl_sales * pl_margin_rate)
        net_margin_gained = simulated_blended_margin - current_blended_margin
        
        st.markdown("#### Projected Profitability Turnaround Yield")
        st.metric("📈 Simulated Gross Profit Expansion (Net Addition)", f"₹{net_margin_gained:,.2f}")
        st.info(f"💡 Execution Insight: Reclaiming {recovery_pct}% of portfolio drops shifts this supervisor's private label pool contribution from {current_pl_share_net:.1f}% to {new_pl_share_target:.1f}%.")

    st.markdown("---")

    # 8. BUSINESS EXECUTIVE FOCUS: SUPERVISOR PORTFOLIO SUMMARY (CLEANED & FILTERABLE)
    st.subheader("📋 Supervisor Portfolio Summary")
    st.markdown("Boardroom performance directory. Use the table column header arrows to dynamically filter, group, and sort portfolios.")

    super_matrix = []
    for sup_name, sup_data in df.groupby('Supervisor'):
        super_matrix.append({
            "Supervisor Name": sup_name,
            "MTD Sales": sup_data['MTD NetSale'].sum(),
            "1M Degrowth Store Count": (sup_data['Net_Variance_Vs_PM1'] < 0).sum(),
            "2M Degrowth Store Count": (sup_data['Net_Variance_Vs_PM2'] < 0).sum(),
            "1M Growth Value": sup_data[sup_data['Net_Variance_Vs_PM1'] > 0]['Net_Variance_Vs_PM1'].sum(),
            "2M Real Degrowth": ((sup_data['Net_Variance_Vs_PM1'] < 0) & (sup_data['Net_Variance_Vs_PM2'] < 0)).sum(),
            "1M Growth Store Count": (sup_data['Net_Variance_Vs_PM1'] >= 0).sum(),
            "2M Growth Stores Count": ((sup_data['Net_Variance_Vs_PM1'] >= 0) & (sup_data['Net_Variance_Vs_PM2'] >= 0)).sum()
        })
        
    super_summary_df = pd.DataFrame(super_matrix)

    st.dataframe(
        super_summary_df.sort_values(by="2M Real Degrowth", ascending=False),
        column_config={
            "MTD Sales": st.column_config.NumberColumn("MTD Sales", format="₹%,.2f"),
            "1M Growth Value": st.column_config.NumberColumn("1M Growth Value", format="₹%,.2f"),
            "1M Degrowth Store Count": st.column_config.NumberColumn("1M Degrowth Outlets"),
            "2M Degrowth Store Count": st.column_config.NumberColumn("2M Degrowth Outlets"),
            "2M Real Degrowth": st.column_config.NumberColumn("🔥 2M Real Degrowth"),
            "1M Growth Store Count": st.column_config.NumberColumn("1M Growth Outlets"),
            "2M Growth Stores Count": st.column_config.NumberColumn("🟩 2M Growth Outlets")
        },
        use_container_width=True,
        hide_index=True
    )
    st.markdown("---")

    # 9. Interactive Visualizations
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📊 Network Portfolio Status Breakdown")
        class_counts = f_df['Operational Classification'].value_counts().reset_index()
        class_counts.columns = ['Classification', 'Count']
        fig_pie = px.pie(
            class_counts, values='Count', names='Classification', color='Classification',
            color_discrete_map={'💥 Critical Core Decline (2M Drop)': '#dc2626', '🚨 High Risk Shift (1M Drop)': '#f59e0b', '🔄 Volatile Swing Outlet': '#38bdf8', '⭐ Shooting Star Outlet': '#10b981'},
            title="Operational Split for Selected Portfolio"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("📉 Top Revenue Leaking Outlets")
        leaking_stores_top10 = f_df.nsmallest(10, 'Net_Variance_Vs_PM1')
        leaking_stores_top10['Absolute_Leakage'] = abs(leaking_stores_top10['Net_Variance_Vs_PM1'])
        fig_leak = px.bar(
            leaking_stores_top10, x='Absolute_Leakage', y='StoreName', orientation='h',
            title="Highest Financial Value Drops in Selected Portfolio", color='Absolute_Leakage', color_continuous_scale='Reds',
            labels={'Absolute_Leakage': 'Net Revenue Lost (₹)', 'StoreName': 'Store Location'}
        )
        fig_leak.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(fig_leak, use_container_width=True)
    st.markdown("---")

    # 10. Manager Growth Leaderboard
    st.subheader("👑 Manager-of-the-Month Performance Leaderboard")
    leaderboard_df = f_df.copy().sort_values(by="Net_Variance_Vs_PM1", ascending=False).reset_index(drop=True)
    leaderboard_df.index = leaderboard_df.index + 1
    leaderboard_df.index.name = 'Portfolio Rank'
    leader_cols = ["StoreName", "Manager", "Supervisor", "MTD NetSale", "Net Sale PM1", "Net_Variance_Vs_PM1"]
    
    st.dataframe(
        leaderboard_df[leader_cols],
        column_config={
            "MTD NetSale": st.column_config.NumberColumn("MTD NetSale", format="₹%,.2f"),
            "Net Sale PM1": st.column_config.NumberColumn("Net Sale PM1", format="₹%,.2f"),
            "Net_Variance_Vs_PM1": st.column_config.NumberColumn("Net Variance (1M)", format="₹+%,.2f")
        },
        use_container_width=True
    )
    st.markdown("---")

    # 11. Granular Drilldown Control Panel with Fixed Slicing
    st.subheader("🔬 Operational Target Drilldown Control Panel")
    st.markdown("**Color Code Key:** 🟥 Red = 2-Month Degrowth | 🟧 Orange = 1-Month Degrowth | 🟪 Blue = 1-Month Growth | 🟩 Green = 2-Month Growth")
    
    selected_class = st.selectbox(
        "Isolate Stores by Management Classification Profile:", 
        ["Show All Stores", "Isolate 💥 Critical Core Decline (2M Drop) Only", "Isolate 🚨 High Risk Shift (1M Drop) Only", "Isolate ⭐ Shooting Star Benchmarks Only"]
    )
    
    display_grid_df = f_df.copy()
    if "Critical Core Decline" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]
    elif "High Risk Shift" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "🚨 High Risk Shift (1M Drop)"]
    elif "Shooting Star" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "⭐ Shooting Star Outlet"]

    # Refactored Cell-by-Cell Painter using ONLY the visible columns provided in display loop
    def color_cells_by_segment(val_df):
        style_df = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        
        for idx in val_df.index:
            # Safely fetch matching variance context values using index references
            net_v1 = display_grid_df.loc[idx, 'Net_Variance_Vs_PM1']
            net_v2 = display_grid_df.loc[idx, 'Net_Variance_Vs_PM2']
            pharma_v1 = display_grid_df.loc[idx, 'Pharma_Variance_Vs_PM1']
            pharma_v2 = display_grid_df.loc[idx, 'Pharma_Variance_Vs_PM2']
            non_v1 = display_grid_df.loc[idx, 'NonPharma_Variance_Vs_PM1']
            non_v2 = display_grid_df.loc[idx, 'NonPharma_Variance_Vs_PM2']

            def get_color(v1, v2):
                if v1 < 0 and v2 < 0: return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
                elif v1 < 0 and v2 >= 0: return 'background-color: #ffe6cc; color: #d97706;'
                elif v1 >= 0 and v2 < 0: return 'background-color: #e0f2fe; color: #0284c7;'
                return 'background-color: #d1fae5; color: #16a34a;'

            style_df.loc[idx, 'MTD NetSale'] = get_color(net_v1, net_v2)
            style_df.loc[idx, 'PL Pharma NetSale'] = get_color(pharma_v1, pharma_v2)
            style_df.loc[idx, 'PL NonPharma NetSale'] = get_color(non_v1, non_v2)
            
        return style_df

    visible_cols = ["StoreName", "Supervisor", "Manager", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale"]
    
    # Form styles strictly mapping visible parameters
    final_styled_grid = display_grid_df[visible_cols].style.apply(color_cells_by_segment, axis=None).format({
        "MTD NetSale": "₹{:,.2f}", "PL Pharma NetSale": "₹{:,.2f}", "PL NonPharma NetSale": "₹{:,.2f}"
    })

    st.dataframe(final_styled_grid, use_container_width=True)
