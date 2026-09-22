# Save this file exactly as app.py inside your project folder
import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. Premium Page Setup
st.set_page_config(page_title="Supervisor Performance Dashboard", layout="wide")
st.title("📊 Supervisor Performance Dashboard")
st.markdown("### Strategic Turnaround Management Network Platform")
st.markdown("---")

# 2. Heavy-Duty Enterprise Data Intake Pipeline
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
        
        # Safe filter for the final ledger totals
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
        st.error(f"Operational Intake Pipeline Failure: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ Operational ledger sheet missing. Verify 'sales_data.csv' position on GitHub.")
else:
    # 3. Advanced Retail Analytics Computation Engine
    df['Net_Variance_Vs_PM1'] = df['MTD NetSale'] - df['Net Sale PM1']
    df['Net_Variance_Vs_PM2'] = df['Net Sale PM1'] - df['Net Sale PM2']
    
    df['Pharma_Variance_Vs_PM1'] = df['PL Pharma NetSale'] - df['Pharma PM1']
    df['Pharma_Variance_Vs_PM2'] = df['Pharma PM1'] - df['Pharma PM2']
    
    df['NonPharma_Variance_Vs_PM1'] = df['PL NonPharma NetSale'] - df['NON Pharma PM1']
    df['NonPharma_Variance_Vs_PM2'] = df['NON Pharma PM1'] - df['NON Pharma PM2']

    # Private Label Capture Penetration Math
    df['Pharma_PL_Share'] = (df['PL Pharma NetSale'] / df['MTD NetSale'].replace(0, 1) * 100).fillna(0.0)

    # 4. Multi-Month Execution Diagnostics & Dynamic Action Generation
    def calculate_classification(row):
        if row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_PM2'] < 0:
            return "💥 Critical Core Decline (2M Drop)"
        elif row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_PM2'] >= 0:
            return "🚨 High Risk Shift (1M Drop)"
        elif row['Net_Variance_Vs_PM1'] >= 0 and row['Net_Variance_Vs_PM2'] < 0:
            return "🔄 Volatile Swing Outlet"
        return "⭐ Shooting Star Outlet"

    def calculate_poa(row):
        actions = []
        if row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_PM2'] < 0:
            actions.append("🚨 [REVENUE CRITICAL] Launch local community health camps to restart customer footfall traffic immediately.")
        elif row['Net_Variance_Vs_PM1'] < 0:
            actions.append("⚠️ [REVENUE DROP] Review counter wait times and morning/evening peak-hour shift compliance.")
        
        if row['Pharma_Variance_Vs_PM1'] < 0 and row['Pharma_Variance_Vs_PM2'] < 0:
            actions.append("💊 [PHARMA CRITICAL] Immediate audit of prescription substitution rates and Private Label upselling.")
        
        if row['NonPharma_Variance_Vs_PM1'] < 0 and row['NonPharma_Variance_Vs_PM2'] < 0:
            actions.append("🛍️ [NON-PHARMA CRITICAL] Restructure cash-counter layout and enforce checkout bundle cross-selling.")
            
        if not actions:
            return "🟢 [STABLE GROWTH] Maintain lines. Document pitch styles to share as training materials for the network."
        return " | ".join(actions)

    df['Operational Classification'] = df.apply(calculate_classification, axis=1)
    df['Strategic Action Plan (POA)'] = df.apply(calculate_poa, axis=1)

    # 5. Core Executive KPIs
    st.subheader("📌 Corporate Network Financial Health Command")
    
    network_gross = df['MTD NetSale'].sum()
    total_leakage = df[df['Net_Variance_Vs_PM1'] < 0]['Net_Variance_Vs_PM1'].sum()
    critical_count = (df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)").sum()
    star_count = (df['Operational Classification'] == "⭐ Shooting Star Outlet").sum()
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric(label="💼 Total Network Gross Sales", value=f"₹{network_gross:,.2f}")
    with metric_col2:
        st.metric(label="📉 Monthly Rupee Value Leakage", value=f"₹{abs(total_leakage):,.2f}", delta="Action Required", delta_color="inverse")
    with metric_col3:
        st.metric(label="🚨 Stores in 2-Month Spiral", value=f"{critical_count} Branches", delta=f"{(critical_count/len(df))*100:.1f}% of network", delta_color="inverse")
    with metric_col4:
        st.metric(label="🏆 Star Benchmark Outlets", value=f"{star_count} Branches", delta="Network Benchmarks")

    st.markdown("---")

    # 6. Strategic Excel Recovery Sheet Exporter
    st.subheader("📥 Export Enterprise Recovery Spreadsheet")
    st.markdown("Download this data to give your district supervisors a clear, prioritized list of which stores are losing the most revenue and what action steps they need to take.")
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as script_writer:
        columns_to_export = [
            "StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", 
            "Net_Variance_Vs_PM1", "Pharma_PL_Share", "Operational Classification", "Strategic Action Plan (POA)"
        ]
        df[columns_to_export].sort_values(by="Net_Variance_Vs_PM1", ascending=True).to_excel(script_writer, sheet_name="Operations Recovery Action", index=False)
        
    st.download_button(
        label="📥 Download Priority Field Recovery Action Ledger (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name="Executive_Retail_Turnaround_Ledger.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    # 7. Portfolio Health by District Supervisor Line
    st.subheader("📋 District Supervisor Strategic Portfolio Summary")
    
    super_ops_summary = df.groupby('Supervisor').agg(
        Managed_Portfolio_Size=('StoreID', 'nunique'),
        Total_Current_Sales=('MTD NetSale', 'sum'),
        Total_Net_Leakage=('Net_Variance_Vs_PM1', lambda x: x[x < 0].sum()),
        Critical_Spiraling_Stores=('Operational Classification', lambda x: (x == "💥 Critical Core Decline (2M Drop)").sum()),
        Star_Outlets_Count=('Operational Classification', lambda x: (x == "⭐ Shooting Star Outlet").sum())
    ).reset_index().sort_values(by="Total_Net_Leakage", ascending=True)

    super_ops_summary.columns = [
        "Supervisor Name", "Portfolio Size (Stores)", "Current Net Performance (₹)", 
        "Total Leakage Value (₹)", "💥 2-Month Decline Count", "⭐ Benchmark Star Count"
    ]

    st.dataframe(
        super_ops_summary.style.format({
            "Current Net Performance (₹)": "₹{:,.2f}",
            "Total Leakage Value (₹)": "₹{:,.2f}"
        }).background_gradient(subset=["Total Leakage Value (₹)"], cmap="Reds_r"),
        use_container_width=True
    )

    st.markdown("---")

    # 8. Interactive Multi-Dimensional Visualizations
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📊 Network Portfolio Status Breakdown")
        class_counts = df['Operational Classification'].value_counts().reset_index()
        class_counts.columns = ['Classification', 'Count']
        
        fig_pie = px.pie(
            class_counts, values='Count', names='Classification',
            color='Classification',
            color_discrete_map={
                '💥 Critical Core Decline (2M Drop)': '#dc2626',
                '🚨 High Risk Shift (1M Drop)': '#f59e0b',
                '🔄 Volatile Swing Outlet': '#38bdf8',
                '⭐ Shooting Star Outlet': '#10b981'
            },
            title="Operational Health Split across Network"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("📉 Top 10 Revenue Leaking Outlets")
        leaking_stores_top10 = df.nsmallest(10, 'Net_Variance_Vs_PM1')
        leaking_stores_top10['Absolute_Leakage'] = abs(leaking_stores_top10['Net_Variance_Vs_PM1'])
        
        fig_leak = px.bar(
            leaking_stores_top10,
            x='Absolute_Leakage',
            y='StoreName',
            orientation='h',
            title="Highest Financial Value Drops (Current Month vs PM1)",
            color='Absolute_Leakage',
            color_continuous_scale='Reds',
            labels={'Absolute_Leakage': 'Net Revenue Lost (₹)', 'StoreName': 'Store Location'}
        )
        fig_leak.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
        st.plotly_chart(fig_leak, use_container_width=True)

    st.markdown("---")

    # 9. Granular Command Ledger Explorer View
    st.subheader("🔬 Operational Target Drilldown Control Panel")
st.markdown("Color Code Key: 🟥 Red = 2-Month Degrowth | 🟧 Orange = 1-Month Degrowth | 🟪 Blue = 1-Month Growth | 🟩 Green = 2-Month Growth")selected_class = st.selectbox("Isolate Stores by Management Classification Profile:",["Show All Stores", "Isolate 💥 Critical Core Decline (2M Drop) Only", "Isolate 🚨 High Risk Shift (1M Drop) Only", "Isolate ⭐ Shooting Star Benchmarks Only"])display_grid_df = df.copy()if "Critical Core Decline" in selected_class:display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]elif "High Risk Shift" in selected_class:display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "🚨 High Risk Shift (1M Drop)"]elif "Shooting Star" in selected_class:display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "⭐ Shooting Star Outlet"]# Segment Cell-by-Cell Background Painting Matrix Enginedef color_cells_by_segment(val_df):style_df = pd.DataFrame('', index=val_df.index, columns=val_df.columns)def match_style(v1, v2):if v1 < 0 and v2 < 0:return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;' # Redelif v1 < 0 and v2 >= 0:return 'background-color: #ffe6cc; color: #d97706;' # Orangeelif v1 >= 0 and v2 < 0:return 'background-color: #e0f2fe; color: #0284c7;' # Blueelse:return 'background-color: #d1fae5; color: #16a34a;' # Greenfor idx in val_df.index:style_df.loc[idx, 'MTD NetSale'] = match_style(val_df.loc[idx, 'Net_Variance_Vs_PM1'], val_df.loc[idx, 'Net_Variance_Vs_PM2'])style_df.loc[idx, 'PL Pharma NetSale'] = match_style(val_df.loc[idx, 'Pharma_Variance_Vs_PM1'], val_df.loc[idx, 'Pharma_Variance_Vs_PM2'])style_df.loc[idx, 'PL NonPharma NetSale'] = match_style(val_df.loc[idx, 'NonPharma_Variance_Vs_PM1'], val_df.loc[idx, 'NonPharma_Variance_Vs_PM2'])return style_dfdisplay_grid_cols = ["StoreName", "Supervisor", "Manager","MTD NetSale", "Net_Variance_Vs_PM1", "Net_Variance_Vs_PM2","PL Pharma NetSale", "Pharma_Variance_Vs_PM1", "Pharma_Variance_Vs_PM2","PL NonPharma NetSale", "NonPharma_Variance_Vs_PM1", "NonPharma_Variance_Vs_PM2","Strategic Action Plan (POA)"]visible_cols = ["StoreName", "Supervisor", "Manager", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale", "Strategic Action Plan (POA)"]final_styled_grid = display_grid_df[display_grid_cols].sort_values(by="Net_Variance_Vs_PM1", ascending=True).style.apply(color_cells_by_segment, axis=None).format({"MTD NetSale": "₹{:,.2f}","PL Pharma NetSale": "₹{:,.2f}","PL NonPharma NetSale": "₹{:,.2f}"})st.dataframe(final_styled_grid, columns=visible_cols, use_container_width=True)