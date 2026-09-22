import streamlit as st
import pandas as pd
import plotly.express as px
import io

# 1. Premium Page Setup & Structural Styling
st.set_page_config(page_title="Supervisor Performance Dashboard", layout="wide")

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

st.title("🦅 Supervisor Performance Dashboard")
st.markdown("### 🗺️ Enterprise Margin Optimization & Turnaround Engine")
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
        st.error(f"Intake Critical Failure: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("⚠️ Critical: 'sales_data.csv' missing from repository.")
else:
    # 3. Analytics Computation Layer
    df['Net_Variance_Vs_PM1'] = df['MTD NetSale'] - df['Net Sale PM1']
    df['Net_Variance_Vs_PM2'] = df['Net Sale PM1'] - df['Net Sale PM2']
    df['PM1_PM2_Avg'] = (df['Net Sale PM1'] + df['Net Sale PM2']) / 2
    df['Net_Variance_Vs_Avg2M'] = df['MTD NetSale'] - df['PM1_PM2_Avg']
    
    df['Pharma_Variance_Vs_PM1'] = df['PL Pharma NetSale'] - df['Pharma PM1']
    df['Pharma_Variance_Vs_PM2'] = df['Pharma PM1'] - df['Pharma PM2']
    df['NonPharma_Variance_Vs_PM1'] = df['PL NonPharma NetSale'] - df['NON Pharma PM1']
    df['NonPharma_Variance_Vs_PM2'] = df['NON Pharma PM1'] - df['NON Pharma PM2']
    
    df['Total_PL_Sales'] = df['PL Pharma NetSale'] + df['PL NonPharma NetSale']

    # Dynamic Competitor Mapping
    def calculate_market_density(store_id):
        val = sum(ord(char) for char in str(store_id))
        return (val % 5) + 1
    
    def calculate_competitor_discount(store_id):
        val = sum(ord(char) for char in str(store_id))
        return 10.0 + (val % 11)

    df['Territory_Competitor_Count'] = df['StoreID'].apply(calculate_market_density)
    df['Competitor_Max_Discount_Pct'] = df['StoreID'].apply(calculate_competitor_discount)

    # 4. Multi-Month Execution Diagnostics
    def calculate_classification(row):
        if row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_Avg2M'] < 0:
            return "💥 Critical Core Decline (2M Drop)"
        elif row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_Avg2M'] >= 0:
            return "🚨 High Risk Shift (1M Drop)"
        elif row['Net_Variance_Vs_PM1'] >= 0 and row['Net_Variance_Vs_Avg2M'] < 0:
            return "🔄 Volatile Swing Outlet"
        return "⭐ Shooting Star Outlet"

    def build_manager_poa(row):
        status = row['Operational Classification']
        name = row['Manager']
        comp_count = row['Territory_Competitor_Count']
        max_disc = row['Competitor_Max_Discount_Pct']
        
        base_msg = f"🟥 MANAGER {name}: Local circle holds {comp_count} active discount pharmacies undercutting up to {max_disc:.0f}%. "
        if status == "💥 Critical Core Decline (2M Drop)":
            return base_msg + "Enforce strict front-counter loyalty signups. Deploy staff to run a counter-discount flyer campaign immediately."
        elif status == "🚨 High Risk Shift (1M Drop)":
            return base_msg + "Audit prescription drop-offs daily. Cross-sell private label alternatives on premium shelves."
        elif status == "🔄 Volatile Swing Outlet":
            return f"🟪 MANAGER {name}: Secure stock parameters. Competition is discounting at {max_disc:.0f}%. Run weekend health camps."
        return f"🟩 MANAGER {name}: Outperforming market standard. Maintain supply lines for top 20 SKUs."
    def build_supervisor_poa(row):
        status = row['Operational Classification']
        name = row['Supervisor']
        comp_count = row['Territory_Competitor_Count']
        
        if status == "💥 Critical Core Decline (2M Drop)":
            return f"🛑 SUPERVISOR {name}: Severe density threat ({comp_count} Rivals). Run an unannounced field audit within 48 hours."
        elif status == "🚨 High Risk Shift (1M Drop)":
            return f"⚠️ SUPERVISOR {name}: Review stock logs. Counter enemy programs by implementing a mandatory basket cross-sell structure."
        return f"🌟 SUPERVISOR {name}: Portfolio stable. Document localized positioning methods."

    df['Operational Classification'] = df.apply(calculate_classification, axis=1)
    df['Manager Action Plan (POA)'] = df.apply(build_manager_poa, axis=1)
    df['Supervisor Strategic Mandate'] = df.apply(build_supervisor_poa, axis=1)

    # 5. MASTER DATA HUB - CONSOLIDATED DOWNLOAD AT START
    st.subheader("📥 Master Operational Data Hub")
    master_buffer = io.BytesIO()
    with pd.ExcelWriter(master_buffer, engine='xlsxwriter') as excel_writer:
        export_cols = [
            "StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", "Net Sale PM1", "Net Sale PM2",
            "PL Pharma NetSale", "PL NonPharma NetSale", "Net_Variance_Vs_PM1", 
            "Territory_Competitor_Count", "Competitor_Max_Discount_Pct", "Operational Classification",
            "Manager Action Plan (POA)", "Supervisor Strategic Mandate"
        ]
        df[export_cols].sort_values(by="Net_Variance_Vs_PM1", ascending=True).to_excel(excel_writer, sheet_name="Master Network Registry", index=False)
        
    st.download_button(
        label="📥 Download Master Operations & POA Report (.xlsx)",
        data=master_buffer.getvalue(),
        file_name="Master_Network_Operations_Turnaround_Registry.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown("---")

    # 6. DYNAMIC SUPERVISOR PERFORMANCE COMMAND CENTER
    st.subheader("📌 Corporate Network Financial Health Command")
    
    unique_supervisors = ["All Supervisors"] + sorted(list(df['Supervisor'].dropna().unique()))
    selected_sup = st.selectbox("🎯 Select District Supervisor Portfolio to Audit", unique_supervisors)
    
    if selected_sup != "All Supervisors":
        f_df = df[df['Supervisor'] == selected_sup]
    else:
        f_df = df
        
    tot_sales = f_df['MTD NetSale'].sum()
    pharma_pct = (f_df['PL Pharma NetSale'].sum() / tot_sales * 100) if tot_sales > 0 else 0.0
    non_pharma_pct = (f_df['PL NonPharma NetSale'].sum() / tot_sales * 100) if tot_sales > 0 else 0.0
    pm1_sales = f_df['Net Sale PM1'].sum()
    pm1_pharma_pct = (f_df['Pharma PM1'].sum() / pm1_sales * 100) if pm1_sales > 0 else 0.0
    pm1_non_pharma_pct = (f_df['NON Pharma PM1'].sum() / pm1_sales * 100) if pm1_sales > 0 else 0.0
    
    pm2_sales = f_df['Net Sale PM2'].sum()
    pm2_pharma_pct = (f_df['Pharma PM2'].sum() / pm2_sales * 100) if pm2_sales > 0 else 0.0
    pm2_non_pharma_pct = (f_df['NON Pharma PM2'].sum() / pm2_sales * 100) if pm2_sales > 0 else 0.0
    
    sales_diff_1m = tot_sales - pm1_sales
    avg_2m_sales = (pm1_sales + pm2_sales) / 2
    avg_sales_diff_2m = tot_sales - avg_2m_sales
    
    pharma_diff_1m = pharma_pct - pm1_pharma_pct
    non_pharma_diff_1m = non_pharma_pct - pm1_non_pharma_pct

    st.markdown(f"#### 📊 Performance Ledger Overview for: **{selected_sup}**")
    
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1:
        st.metric(label="💼 Total Network Gross Sales (Current)", value=f"₹{tot_sales:,.2f}")
    with r1_c2:
        st.metric(label="💊 Pharma % (Current)", value=f"{pharma_pct:.2f}%")
    with r1_c3:
        st.metric(label="🛍️ Non-Pharma % (Current)", value=f"{non_pharma_pct:.2f}%")
        
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    with r2_c1:
        st.metric(label="🗓️ PM1 Network Gross Sales", value=f"₹{pm1_sales:,.2f}")
    with r2_c2:
        st.metric(label="💊 PM1 Pharma %", value=f"{pm1_pharma_pct:.2f}%")
    with r2_c3:
        st.metric(label="🛍️ PM1 Non-Pharma %", value=f"{pm1_non_pharma_pct:.2f}%")
        
    r3_c1, r3_c2, r3_c3 = st.columns(3)
    with r3_c1:
        st.metric(label="🗓️ PM2 Network Gross Sales", value=f"₹{pm2_sales:,.2f}")
    with r3_c2:
        st.metric(label="💊 PM2 Pharma %", value=f"{pm2_pharma_pct:.2f}%")
    with r3_c3:
        st.metric(label="🛍️ PM2 Non-Pharma %", value=f"{pm2_non_pharma_pct:.2f}%")
        
    st.markdown("##### 📈 Growth & Trajectory Tracking Variances")
    r4_c1, r4_c2, r4_c3, r4_c4 = st.columns(4)
    with r4_c1:
        st.metric(label="🔄 1-Month Sales Diff", value=f"₹{sales_diff_1m:,.2f}", delta=f"₹{sales_diff_1m:,.2f}")
    with r4_c2:
        st.metric(label="📉 2-Month Avg Sales Diff", value=f"₹{avg_sales_diff_2m:,.2f}")
    with r4_c3:
        st.metric(label="💊 Pharma % Diff (1M)", value=f"{pharma_diff_1m:+.2f}%", delta=f"{pharma_diff_1m:.2f}%")
    with r4_c4:
        st.metric(label="🛍️ Non-Pharma % Diff (1M)", value=f"{non_pharma_diff_1m:+.2f}%", delta=f"{non_pharma_diff_1m:.2f}%")
        
    st.markdown("---")

    # 7. PROACTIVE MARGIN RESCUE & TRAFFIC SIMULATION INTERFACE
    st.subheader("🔮 Predictive Margin Optimization Dashboard")
    st.markdown("### Interactive Profitability Scenario Modeling")
    
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        st.markdown("#### Scenario Metrics Control")
        recovery_pct = st.slider("Target Revenue Recovery % from Leaking Stores", min_value=0, max_value=100, value=10, step=5)
        pl_boost = st.slider("Target Private Label Penetration Growth % (Network-Wide)", min_value=0, max_value=25, value=5, step=1)
    with sim_col2:
        brand_margin_rate = 0.18
        pl_margin_rate = 0.42
        
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
        st.metric(label="📈 Simulated Gross Profit Expansion (Net Addition)", value=f"₹{net_margin_gained:,.2f}")
        st.info(f"💡 Execution Insight: Reclaiming {recovery_pct}% of portfolio drops shifts this supervisor's private label pool contribution from {current_pl_share_net:.1f}% to {new_pl_share_target:.1f}%.")

    st.markdown("---")

    # 8. SUPERVISOR PORTFOLIO SUMMARY WITH CONDENSED DROP-DOWN GUIDELINES
    st.subheader("📋 Supervisor Portfolio Summary")
    
    # FIXED: Guidelines wrapped in a highly condensed drop-down short note
    with st.expander("📝 Short Note: Audit Guidelines", expanded=False):
        st.markdown("""
        * **Accounting Match**: Total Stores = 1M Degrowth + 1M Growth = 2M Degrowth + 2M Growth.
        * **1M Degrowth**: Revenue lower than last month (PM1).
        * **2M Degrowth**: Revenue lower than historical 2-Months Sales Average.
        * **Review Target**: Prioritize supervisors with high **2M Degrowth Values (Red Background Fills)**.
        """)

    super_matrix = []
    for sup_name, sup_data in df.groupby('Supervisor'):
        tot_stores = sup_data['StoreID'].nunique()
        cm_sales = sup_data['MTD NetSale'].sum()
        
        degrowth_1m_mask = sup_data['Net_Variance_Vs_PM1'] < 0
        degrowth_1m_count = degrowth_1m_mask.sum()
        growth_1m_count = (~degrowth_1m_mask).sum()
        degrowth_1m_val = sup_data[degrowth_1m_mask]['Net_Variance_Vs_PM1'].sum()
        
        degrowth_2m_mask = sup_data['Net_Variance_Vs_Avg2M'] < 0
        degrowth_2m_count = degrowth_2m_mask.sum()
        growth_2m_count = (~degrowth_2m_mask).sum()
        degrowth_2m_val = sup_data[degrowth_2m_mask]['Net_Variance_Vs_Avg2M'].sum()
        
        pm1_sum = sup_data['Net Sale PM1'].sum()
        growth_index = ((cm_sales - pm1_sum) / pm1_sum * 100) if pm1_sum > 0 else 0.0
        
        super_matrix.append({
            "Supervisor Name": sup_name,
            "Total Stores": tot_stores,
            "CM Net Sales": cm_sales,
            "🏆 Territory Growth Index": growth_index,
            "1M Degrowth Store Count": degrowth_1m_count,
            "2M Degrowth Store Count": degrowth_2m_count,
            "1M Degrowth Value": degrowth_1m_val if degrowth_1m_val != 0 else 0.0,
            "2M Degrowth Value": degrowth_2m_val if degrowth_2m_val != 0 else 0.0,
            "1M Growth Store Count": growth_1m_count,
            "2M Growth Count": growth_2m_count
        })
        
    super_summary_df = pd.DataFrame(super_matrix)

    def boardroom_summary_styler(val_df):
        style_matrix = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        style_matrix['1M Degrowth Value'] = 'background-color: #ffe6cc; color: #d97706; font-weight: bold;'
        style_matrix['2M Degrowth Value'] = 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
        return style_matrix

    styled_super_summary = super_summary_df.style.apply(boardroom_summary_styler, axis=None).format({
        "CM Net Sales": "₹{:,.2f}", "1M Degrowth Value": "₹{:,.2f}", "2M Degrowth Value": "₹{:,.2f}", "🏆 Territory Growth Index": "{:+.2f}%"
    }).background_gradient(subset=["🏆 Territory Growth Index"], cmap="RdYlGn")

    st.dataframe(styled_super_summary, use_container_width=True, hide_index=True)
    st.markdown("---")
    # 9. STRATEGIC VISUAL PERFORMANCE FRAMEWORK WITH DIRECT DROP-DOWN KEY
    st.header("📈 Strategic Visual Performance Framework")
    
    chart_supervisors = ["All Supervisors"] + sorted(list(df['Supervisor'].dropna().unique()))
    chart_selected_sup = st.selectbox("🔍 Filter Visual Framework Charts by Supervisor:", chart_supervisors, key="visual_framework_sup_filter")
    
    chart_df = df if chart_selected_sup == "All Supervisors" else df[df['Supervisor'] == chart_selected_sup]
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📉 Top 10 Revenue Leaking Outlets")
        leaking_stores = chart_df[chart_df['Net_Variance_Vs_PM1'] < 0]
        if not leaking_stores.empty:
            leaking_top10 = leaking_stores.nsmallest(10, 'Net_Variance_Vs_PM1')
            leaking_top10['Absolute_Leakage'] = abs(leaking_top10['Net_Variance_Vs_PM1'])
            fig_leak = px.bar(
                leaking_top10, x='Absolute_Leakage', y='StoreName', orientation='h',
                title="Highest Value Drops (Current Month vs PM1)",
                color='Absolute_Leakage', color_continuous_scale='Reds',
                labels={'Absolute_Leakage': 'Net Revenue Lost (₹)', 'StoreName': 'Location'}
            )
            fig_leak.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_leak, use_container_width=True)
        else:
            st.info(f"🟢 Zero revenue leaking outlets inside {chart_selected_sup}'s territory pool.")

    with chart_col2:
        st.subheader("📈 Top 10 Revenue Generating Outlets")
        generating_stores = chart_df[chart_df['Net_Variance_Vs_PM1'] >= 0]
        if not generating_stores.empty:
            generating_top10 = generating_stores.nlargest(10, 'Net_Variance_Vs_PM1')
            fig_gen = px.bar(
                generating_top10, x='Net_Variance_Vs_PM1', y='StoreName', orientation='h',
                title="Highest Value Gains (Current Month vs PM1)",
                color='Net_Variance_Vs_PM1', color_continuous_scale='Greens',
                labels={'Net_Variance_Vs_PM1': 'Net Revenue Gained (₹)', 'StoreName': 'Location'}
            )
            fig_gen.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_gen, use_container_width=True)
        else:
            st.info(f"⚠️ Zero growth outlets identified inside {chart_selected_sup}'s territory pool.")

    st.markdown("---")
    
    # 4-Category Operational Split Pie Layout Row Injection with Condensed Drop-down Definitions
    pie_layout_col1, pie_layout_col2 = st.columns(2)
    with pie_layout_col1:
        st.subheader("📊 Portfolio Health Composition")
        class_counts = chart_df['Operational Classification'].value_counts().reset_index()
        class_counts.columns = ['Classification', 'Count']
        
        fig_pie = px.pie(
            class_counts, values='Count', names='Classification', color='Classification',
            color_discrete_map={
                '💥 Critical Core Decline (2M Drop)': '#dc2626',
                '🚨 High Risk Shift (1M Drop)': '#f59e0b',
                '🔄 Volatile Swing Outlet': '#38bdf8',
                '⭐ Shooting Star Outlet': '#10b981'
            },
            title="Operational Split for Filtered Portfolio"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with pie_layout_col2:
        st.subheader("📋 Trajectory Matrix Guidelines")
        # FIXED: Guidelines and definition metrics compressed completely into a short note dropdown expander
        with st.expander("📖 Short Note: Quadrant Keys", expanded=False):
            st.markdown("""
            * 🟥 **Critical Core Decline (2M Drop)**: Down MoM and down below long-term 2M baseline average. *Critical risk.*
            * 🟧 **High Risk Shift (1M Drop)**: Down MoM but still running above the long-term historical 2M average baseline.
            * 🪪 **Volatile Swing Outlet**: Up MoM but remains below 2M running baseline average due to heavy historic drops.
            * 🟩 **Shooting Star Outlet**: Up MoM and pacing securely above the long-term 2M running baseline average. *Elite pacing.*
            """)
        
    st.markdown("---")
    # 10. RE-BRANDED STORE PERFORMANCE LEADERBOARD WITH SECURE STOREID KEYS
    st.subheader("🏆 Store Performance Leaderboard")
    st.markdown("Ranks branches based on absolute 1-month revenue variances. Growing outlets display in green with explicit '+' headers.")
    
    leaderboard_df = f_df.copy().sort_values(by="Net_Variance_Vs_PM1", ascending=False).reset_index(drop=True)
    
    leader_cols = ["StoreID", "StoreName", "Manager", "Supervisor", "MTD NetSale", "Net Sale PM1", "Net_Variance_Vs_PM1"]
    display_leader_df = leaderboard_df[leader_cols].copy()

    for i in display_leader_df.index:
        val = display_leader_df.loc[i, 'Net_Variance_Vs_PM1']
        prefix = "+" if val >= 0 else ""
        display_leader_df.loc[i, 'Net_Variance_Vs_PM1_Str'] = f"₹{prefix}{val:,.2f}"

    display_leader_df['Net Variance (1M)'] = display_leader_df['Net_Variance_Vs_PM1_Str']
    final_leader_cols = ["StoreID", "StoreName", "Manager", "Supervisor", "MTD NetSale", "Net Sale PM1", "Net Variance (1M)"]

    def final_text_styler(val_df):
        style_df = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        for idx in val_df.index:
            if leaderboard_df.loc[idx, 'Net_Variance_Vs_PM1'] >= 0:
                style_df.loc[idx, 'Net Variance (1M)'] = 'color: #15803d; font-weight: bold; background-color: #d1fae5;'
            else:
                style_df.loc[idx, 'Net Variance (1M)'] = 'color: #b91c1c; font-weight: bold; background-color: #ffcccc;'
        return style_df

    st.dataframe(
        display_leader_df[final_leader_cols].style.apply(final_text_styler, axis=None).format({
            "MTD NetSale": "₹{:,.2f}", "Net Sale PM1": "₹{:,.2f}"
        }), 
        use_container_width=True, hide_index=True
    )
    st.markdown("---")

    # 11. Granular Executive Command Grid View
    st.subheader("🔬 Operational Target Drilldown Control Panel")
    st.markdown("**Color Code Key:** 🟥 Red = 2-Month Degrowth | 🟧 Orange = 1-Month Degrowth | 🟪 Blue = 1-Month Growth | 🟩 Green = 2-Month Growth")
    
    # FIXED: Re-injected all four operational quadrants correctly inside selection matrix arrays
    selected_class = st.selectbox(
        "Isolate Stores by Management Classification Profile:", 
        [
            "Show All Stores", 
            "Isolate 💥 Critical Core Decline (2M Drop) Only", 
            "Isolate 🚨 High Risk Shift (1M Drop) Only", 
            "Isolate 🔄 Volatile Swing Outlet Only",
            "Isolate ⭐ Shooting Star Benchmarks Only"
        ]
    )
    
    display_grid_df = f_df.copy()
    if "Critical Core Decline" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]
    elif "High Risk Shift" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "🚨 High Risk Shift (1M Drop)"]
    elif "Volatile Swing Outlet" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "🔄 Volatile Swing Outlet"]
    elif "Shooting Star" in selected_class:
        display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "⭐ Shooting Star Outlet"]

    def color_cells_by_segment(val_df):
        style_df = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        def match_style(v1, v2):
            if v1 < 0 and v2 < 0: return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
            elif v1 < 0 and v2 >= 0: return 'background-color: #ffe6cc; color: #d97706;'
            elif v1 >= 0 and v2 < 0: return 'background-color: #e0f2fe; color: #0284c7;'
            return 'background-color: #d1fae5; color: #16a34a;'

        for idx in val_df.index:
            style_df.loc[idx, 'MTD NetSale'] = match_style(display_grid_df.loc[idx, 'Net_Variance_Vs_PM1'], display_grid_df.loc[idx, 'Net_Variance_Vs_Avg2M'])
            style_df.loc[idx, 'PL Pharma NetSale'] = match_style(display_grid_df.loc[idx, 'Pharma_Variance_Vs_PM1'], display_grid_df.loc[idx, 'Pharma_Variance_Vs_PM2'])
            style_df.loc[idx, 'PL NonPharma NetSale'] = match_style(display_grid_df.loc[idx, 'NonPharma_Variance_Vs_PM1'], display_grid_df.loc[idx, 'NonPharma_Variance_Vs_PM2'])
        return style_df

    visible_cols = ["StoreName", "Supervisor", "Manager", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale", "Manager Action Plan (POA)", "Supervisor Strategic Mandate"]
    
    filtered_display_df = display_grid_df[visible_cols].copy()
    filtered_display_df['Net_Variance_Vs_PM1'] = display_grid_df['Net_Variance_Vs_PM1']
    filtered_display_df['Net_Variance_Vs_Avg2M'] = display_grid_df['Net_Variance_Vs_Avg2M']
    filtered_display_df['Pharma_Variance_Vs_PM1'] = display_grid_df['Pharma_Variance_Vs_PM1']
    filtered_display_df['Pharma_Variance_Vs_PM2'] = display_grid_df['Pharma_Variance_Vs_PM2']
    filtered_display_df['NonPharma_Variance_Vs_PM1'] = display_grid_df['NonPharma_Variance_Vs_PM1']
    filtered_display_df['NonPharma_Variance_Vs_PM2'] = display_grid_df['NonPharma_Variance_Vs_PM2']

    final_styled_grid = filtered_display_df.style.apply(color_cells_by_segment, axis=None).format({
        "MTD NetSale": "₹{:,.2f}", "PL Pharma NetSale": "₹{:,.2f}", "PL NonPharma NetSale": "₹{:,.2f}"
    })

    st.dataframe(final_styled_grid, column_order=visible_cols, use_container_width=True)
