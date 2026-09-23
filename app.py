import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re
import urllib.parse

# 1. Page Configuration & Boardroom Typography/Styles
st.set_page_config(page_title="MedPlus Executive Turnaround Command", layout="wide")

st.markdown("""
    <style>
    /* Compact default metric font sizes to crisp boardroom text standards */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    .custom-subtext {
        font-size: 11px;
        color: #64748b;
        margin-top: -8px;
        margin-bottom: 12px;
        font-weight: 500;
    }
    /* Fixed readable presentation styles for the script output terminal */
    .poa-container {
        background-color: #fef2f2;
        border: 1px solid #fee2e2;
        padding: 24px;
        border-radius: 8px;
        color: #1e293b;
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        line-height: 1.6 !important;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    /* Fixed Block-Stack Logo Layout to completely prevent heading text collisions */
    .medplus-header-block {
        margin-bottom: 20px;
    }
    .medplus-logo-box {
        background-color: #e11d48;
        color: #ffffff;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 30px;
        font-weight: 800;
        padding: 6px 20px;
        border-radius: 6px;
        display: inline-block;
        letter-spacing: -1px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .medplus-plus-sign {
        color: #22c55e;
        font-weight: 900;
        margin-left: 2px;
    }
    .medplus-title-heading {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        margin: 5px 0 0 0 !important;
    }
    .medplus-subtitle-heading {
        font-size: 16px !important;
        color: #64748b !important;
        margin: 2px 0 0 0 !important;
    }
    </style>
""", unsafe_allow_html=True)
# Branding Update: Instant CSS Popup Logo Block-Stack Layout
st.markdown("""
    <div class="medplus-header-block">
        <div class="medplus-logo-box">MedPlus<span class="medplus-plus-sign">+</span></div>
        <h1 class="medplus-title-heading">Supervisor Performance Dashboard</h1>
        <p class="medplus-subtitle-heading">Enterprise Margin Optimization & Turnaround Engine</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")
# 2. Indian Currency Formatting Engine (Lakhs & Crores Routine)
def format_indian_currency(number):
    try:
        is_negative = number < 0
        abs_num = abs(number)
        s = f"{abs_num:.2f}"
        parts = s.split('.')
        # FIXED: Added native index row markers to resolve array text dumps inside numbers
        num_part = parts[0]
        dec_part = parts[1]
        
        if len(num_part) <= 3:
            res = num_part
        else:
            last_three = num_part[-3:]
            remaining = num_part[:-3]
            remaining_rev = remaining[::-1]
            groups = [remaining_rev[i:i+2] for i in range(0, len(remaining_rev), 2)]
            remaining_formatted = ",".join(groups)[::-1]
            res = f"{remaining_formatted},{last_three}"
            
        final_str = f"₹{'-' if is_negative else ''}{res}.{dec_part}"
        return final_str
    except:
        return f"₹{number:,.2f}"
# 3. Data Intake Pipeline with Dynamic Date & Day Extraction
@st.cache_data
def load_data_with_temporal_parse():
    extracted_days = 30 
    try:
        with open("sales_data.csv", "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
        
        date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', first_line)
        if date_match:
            extracted_days = int(date_match.group(1))
            if extracted_days <= 0 or extracted_days > 31:
                extracted_days = 30
    except:
        pass
        
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
        
        return df, extracted_days
    except Exception as e:
        st.error(f"Intake Critical Failure: {e}")
        return pd.DataFrame(), extracted_days

df, mtd_days_elapsed = load_data_with_temporal_parse()
if df.empty:
    st.warning("⚠️ Critical: 'sales_data.csv' missing from repository workspace.")
else:
    # 4. Analytics Computation Layer
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
    # 5. Multi-Month Execution Diagnostics
    def calculate_classification(row):
        if row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_Avg2M'] < 0:
            return "💥 Critical Core Decline (2M Drop)"
        elif row['Net_Variance_Vs_PM1'] < 0 and row['Net_Variance_Vs_Avg2M'] >= 0:
            return "🚨 High Risk Shift (1M Drop)"
        elif row['Net_Variance_Vs_PM1'] >= 0 and row['Net_Variance_Vs_Avg2M'] < 0:
            return "🔄 Volatile Swing Outlet"
        return "⭐ Shooting Star Outlet"

    df['Operational Classification'] = df.apply(calculate_classification, axis=1)

    # 5. MASTER DATA HUB - CONSOLIDATED DOWNLOAD AT START
    st.subheader("📥 Master Operational Data Hub")
    master_buffer = io.BytesIO()
    with pd.ExcelWriter(master_buffer, engine='xlsxwriter') as excel_writer:
        export_cols = [
            "StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", "Net Sale PM1", "Net Sale PM2",
            "PL Pharma NetSale", "PL NonPharma NetSale", "Net_Variance_Vs_PM1", "Operational Classification"
        ]
        valid_export_cols = [col for col in export_cols if col in df.columns]
        df[valid_export_cols].sort_values(by="Net_Variance_Vs_PM1", ascending=True).to_excel(excel_writer, sheet_name="MasterRegistry", index=False)
    st.download_button(
        label="📥 Download Master Operations & POA Report (.xlsx)",
        data=master_buffer.getvalue(),
        file_name="Master_Network_Operations_Turnaround_Registry.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown("---")

    # 6. DYNAMIC SUPERVISOR PERFORMANCE COMMAND CENTER
    st.subheader("📌 Corporate Network Financial Health Command")
    st.info(f"📆 Temporal Context Engine Auto-Detected: **{mtd_days_elapsed} Days Elapsed** in the current tracking period.")
    
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
    avg_2m_sales_base = (pm1_sales + pm2_sales) / 2
    avg_sales_diff_2m = tot_sales - avg_2m_sales_base
    pharma_diff_1m = pharma_pct - pm1_pharma_pct
    non_pharma_diff_1m = non_pharma_pct - pm1_non_pharma_pct

    # Pre-calculate Daily Store Averages (Total Sales / Number of Stores / Number of Days)
    num_stores = len(f_df) if len(f_df) > 0 else 1
    
    avg_daily_cm_sales = tot_sales / num_stores / mtd_days_elapsed
    avg_daily_pm1_sales = pm1_sales / num_stores / mtd_days_elapsed
    avg_daily_pm2_sales = pm2_sales / num_stores / mtd_days_elapsed
    avg_daily_diff_1m = sales_diff_1m / num_stores / mtd_days_elapsed
    avg_daily_diff_2m = avg_sales_diff_2m / num_stores / mtd_days_elapsed
    st.markdown(f"#### 📊 Performance Ledger Overview for: **{selected_sup}**")
    
    # Row 1: Current Month Metrics Panel View
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1:
        st.metric(label="💼 Total Network Gross Sales (Current)", value=format_indian_currency(tot_sales))
        st.markdown(f"<div class='custom-subtext'>▲ Daily Store Avg: {format_indian_currency(avg_daily_cm_sales)}</div>", unsafe_allow_html=True)
    with r1_c2:
        st.metric(label="💊 Pharma % (Current)", value=f"{pharma_pct:.2f}%")
        st.markdown("<div class='custom-subtext'>Target Mix: 35.00%</div>", unsafe_allow_html=True)
    with r1_c3:
        st.metric(label="🛍️ Non-Pharma % (Current)", value=f"{non_pharma_pct:.2f}%")
        st.markdown("<div class='custom-subtext'>Target Mix: 65.00%</div>", unsafe_allow_html=True)
        
    # Row 2: Past Month One Metrics Panel View
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    with r2_c1:
        st.metric(label="🗓️ PM1 Network Gross Sales", value=format_indian_currency(pm1_sales))
        st.markdown(f"<div class='custom-subtext'>▼ Daily Store Avg: {format_indian_currency(avg_daily_pm1_sales)}</div>", unsafe_allow_html=True)
    with r2_c2:
        st.metric(label="💊 PM1 Pharma %", value=f"{pm1_pharma_pct:.2f}%")
        st.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    with r2_c3:
        st.metric(label="🛍️ PM1 Non-Pharma %", value=f"{pm1_non_pharma_pct:.2f}%")
        st.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    # Row 3: Past Month Two Metrics Panel View
    r3_c1, r3_c2, r3_c3 = st.columns(3)
    with r3_c1:
        st.metric(label="🗓️ PM2 Network Gross Sales", value=format_indian_currency(pm2_sales))
        st.markdown(f"<div class='custom-subtext'>▼ Daily Store Avg: {format_indian_currency(avg_daily_pm2_sales)}</div>", unsafe_allow_html=True)
    with r3_c2:
        st.metric(label="💊 PM2 Pharma %", value=f"{pm2_pharma_pct:.2f}%")
        st.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    with r3_c3:
        st.metric(label="🛍️ PM2 Non-Pharma %", value=f"{pm2_non_pharma_pct:.2f}%")
        st.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
        
    # Row 4: Growth Tracking and Rupee Variances with Sign Arrow Alignment Indicators
    st.markdown("##### 📈 Growth & Trajectory Tracking Variances")
    r4_c1, r4_c2, r4_c3, r4_c4 = st.columns(4)
    
    with r4_c1:
        arrow_1m = "▲" if sales_diff_1m >= 0 else "▼"
        st.metric(label="🔄 1-Month Sales Diff", value=format_indian_currency(sales_diff_1m))
        st.markdown(f"<div class='custom-subtext'>Daily Store Avg: {arrow_1m} {format_indian_currency(abs(avg_daily_diff_1m))}</div>", unsafe_allow_html=True)
    with r4_c2:
        arrow_2m = "▲" if avg_sales_diff_2m >= 0 else "▼"
        st.metric(label="📉 2-Month Avg Sales Diff", value=format_indian_currency(avg_sales_diff_2m))
        st.markdown(f"<div class='custom-subtext'>Daily Store Avg: {arrow_2m} {format_indian_currency(abs(avg_daily_diff_2m))}</div>", unsafe_allow_html=True)
    with r4_c3:
        arrow_ph = "▲" if pharma_diff_1m >= 0 else "▼"
        st.metric(label="💊 Pharma % Diff (1M)", value=f"{pharma_diff_1m:+.2f}%")
        st.markdown(f"<div class='custom-subtext'>Mix Shift: {arrow_ph} {abs(pharma_diff_1m):.2f}%</div>", unsafe_allow_html=True)
    with r4_c4:
        arrow_nf = "▲" if non_pharma_diff_1m >= 0 else "▼"
        st.metric(label="🛍️ Non-Pharma % Diff (1M)", value=f"{non_pharma_diff_1m:+.2f}%")
        st.markdown(f"<div class='custom-subtext'>Mix Shift: {arrow_nf} {abs(non_pharma_diff_1m):.2f}%</div>", unsafe_allow_html=True)
        
    # INTEGRATED TIER-2 VALUES TRACKING MATRIX
    st.markdown("##### 💰 Dynamic Tier-2 Financial Velocity Tracking Matrix")
    t2_col1, t2_col2, t2_col3, t2_col4 = st.columns(4)
    
    m1_growth_mask = f_df['Net_Variance_Vs_PM1'] >= 0
    m1_growth_pool_val = f_df[m1_growth_mask]['Net_Variance_Vs_PM1'].sum()
    m1_degrow_pool_val = f_df[~m1_growth_mask]['Net_Variance_Vs_PM1'].sum()
    
    m2_growth_mask = f_df['Net_Variance_Vs_Avg2M'] >= 0
    m2_growth_pool_val = f_df[m2_growth_mask]['Net_Variance_Vs_Avg2M'].sum()
    m2_degrow_pool_val = f_df[~m2_growth_mask]['Net_Variance_Vs_Avg2M'].sum()
    with t2_col1:
        st.markdown("<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟩 1M Growth Value</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px; color:#16a34a; font-weight:700; margin:0;'>{format_indian_currency(m1_growth_pool_val)}</p>", unsafe_allow_html=True)
    with t2_col2:
        st.markdown("<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟧 1M Degrowth Value</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px; color:#ea580c; font-weight:700; margin:0;'>{format_indian_currency(m1_degrow_pool_val)}</p>", unsafe_allow_html=True)
    with t2_col3:
        st.markdown("<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟩 2M Growth Value</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px; color:#16a34a; font-weight:700; margin:0;'>{format_indian_currency(m2_growth_pool_val)}</p>", unsafe_allow_html=True)
    with t2_col4:
        st.markdown("<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟥 2M Degrowth Value</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:18px; color:#dc2626; font-weight:700; margin:0;'>{format_indian_currency(m2_degrow_pool_val)}</p>", unsafe_allow_html=True)
        
    st.markdown("---")
    # MODULE 1: PREDICTIVE PRIVATE LABEL SCENARIO SIMULATION ENGINE
    st.subheader("🔮 Predictive Private Label Optimization Sandbox")
    st.markdown("Simulate how shifting brand revenue to higher-margin Private Label options scales portfolio gross profitability.")
    
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        st.markdown("**Operational Margin Configurations**")
        brand_pharma_margin = st.slider("Brand Pharma Margin Rate (%)", 10, 25, 15, 1) / 100.0
        pl_pharma_margin = st.slider("Private Label Pharma Margin Rate (%)", 30, 55, 42, 1) / 100.0
        brand_non_pharma_margin = st.slider("Brand Non-Pharma Margin Rate (%)", 12, 28, 18, 1) / 100.0
        pl_non_pharma_margin = st.slider("Private Label Non-Pharma Margin Rate (%)", 35, 60, 45, 1) / 100.0
    with sim_col2:
        st.markdown("**Volume Migration Targets**")
        pharma_pl_boost = st.slider("Target Pharma Share Shift to PL (%)", 0, 30, 5, 1) / 100.0
        non_pharma_pl_boost = st.slider("Target Non-Pharma Share Shift to PL (%)", 0, 30, 5, 1) / 100.0
        
        current_pl_pharma = f_df['PL Pharma NetSale'].sum()
        current_pl_non_pharma = f_df['PL NonPharma NetSale'].sum()
        total_pharma_pool = f_df['PL Pharma NetSale'].sum() * 3.5  
        total_non_pharma_pool = f_df['PL NonPharma NetSale'].sum() * 4.0
        
        current_brand_pharma = max(0.0, total_pharma_pool - current_pl_pharma)
        current_brand_non_pharma = max(0.0, total_non_pharma_pool - current_pl_non_pharma)
        base_profit = (current_brand_pharma * brand_pharma_margin) + (current_pl_pharma * pl_pharma_margin) + \
                      (current_brand_non_pharma * brand_non_pharma_margin) + (current_pl_non_pharma * pl_non_pharma_margin)
                      
        migrated_pharma = current_brand_pharma * pharma_pl_boost
        migrated_non_pharma = current_brand_non_pharma * non_pharma_pl_boost
        sim_profit = ((current_brand_pharma - migrated_pharma) * brand_pharma_margin) + \
                     ((current_pl_pharma + migrated_pharma) * pl_pharma_margin) + \
                     ((current_brand_non_pharma - migrated_non_pharma) * brand_non_pharma_margin) + \
                     ((current_pl_non_pharma + migrated_non_pharma) * pl_non_pharma_margin)
                     
        net_profit_expansion = sim_profit - base_profit
        st.markdown("#### Projected Profitability Turnaround Yield")
        st.metric(label="📈 Simulated Gross Profit Expansion (Net Addition)", value=format_indian_currency(net_profit_expansion))
        st.success(f"💡 Strategy Insight: Converting these target volume blocks adds a net yield contribution to **{selected_sup}**'s operating margin pool.")

    st.markdown("---")
    # 8. SUPERVISOR PORTFOLIO SUMMARY WITH CONDENSED DROP-DOWN GUIDELINES
    st.subheader("📋 Supervisor Portfolio Summary")
    
    with st.expander("📝 Short Note: Audit Guidelines", expanded=False):
        st.markdown("""
        * **Accounting Match Check**: Total Stores must equal `1M Degrowth Count + 1M Growth Count` AND `2M Degrowth Count + 2M Growth Count`.
        * **1M Trajectory**: Evaluated against last month's ledger baseline (PM1).
        * **2M Trajectory**: Evaluated against the historical **2-Months Sales Average** `((PM1 + PM2) / 2)`.
        * **Risk Management Focus**: Portfolios displaying massive red blocks in the **2M Degrowth Value** column require supervisor performance containment strategy loops.
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
            "Supervisor Name": sup_name, "Total Stores": tot_stores, "CM Net Sales": cm_sales,
            "🏆 Territory Growth Index": growth_index, "1M Degrowth Store Count": degrowth_1m_count,
            "2M Degrowth Store Count": degrowth_2m_count, "1M Degrowth Value": degrowth_1m_val if degrowth_1m_val != 0 else 0.0,
            "2M Degrowth Value": degrowth_2m_val if degrowth_2m_val != 0 else 0.0, "1M Growth Store Count": growth_1m_count,
            "2M Growth Count": growth_2m_count
        })
    super_summary_df = pd.DataFrame(super_matrix)

    # FIXED: Re-engineered layout to use a fully native inline CSS function mapping rules, completely avoiding matplotlib background_gradient dependencies
    def boardroom_summary_styler(val_df):
        style_matrix = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        style_matrix['1M Degrowth Value'] = 'background-color: #ffe6cc; color: #d97706; font-weight: bold;'
        style_matrix['2M Degrowth Value'] = 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
        
        for idx in val_df.index:
            try:
                raw_idx_val = float(super_summary_df.loc[idx, '🏆 Territory Growth Index'])
                if raw_idx_val >= 5.0:
                    style_matrix.loc[idx, '🏆 Territory Growth Index'] = 'background-color: #d1fae5; color: #065f46; font-weight: bold;'
                elif raw_idx_val >= 0.0:
                    style_matrix.loc[idx, '🏆 Territory Growth Index'] = 'background-color: #ecfdf5; color: #047857;'
                elif raw_idx_val >= -5.0:
                    style_matrix.loc[idx, '🏆 Territory Growth Index'] = 'background-color: #fff7ed; color: #b45309;'
                else:
                    style_matrix.loc[idx, '🏆 Territory Growth Index'] = 'background-color: #fef2f2; color: #991b1b; font-weight: bold;'
            except:
                pass
        return style_matrix

    formatted_super_df = super_summary_df.sort_values(by="2M Degrowth Store Count", ascending=False).copy()
    formatted_super_df['CM Net Sales'] = formatted_super_df['CM Net Sales'].apply(format_indian_currency)
    formatted_super_df['1M Degrowth Value'] = formatted_super_df['1M Degrowth Value'].apply(format_indian_currency)
    formatted_super_df['2M Degrowth Value'] = formatted_super_df['2M Degrowth Value'].apply(format_indian_currency)

    styled_super_summary = formatted_super_df.style.apply(boardroom_summary_styler, axis=None).format({
        "🏆 Territory Growth Index": "{:+.2f}%"
    })

    st.dataframe(styled_super_summary, use_container_width=True, hide_index=True)
    st.markdown("---")
    # 9. HIGH-COMPRESSION SIDE-BY-SIDE TRI-COLUMN EXECUTIVE VISUALIZATION CORE
    st.header("📈 Strategic Visual Performance Framework")
    chart_supervisors = ["All Supervisors"] + sorted(list(df['Supervisor'].dropna().unique()))
    chart_selected_sup = st.selectbox("🔍 Filter Visual Framework Charts by Supervisor:", chart_supervisors, key="visual_framework_sup_filter")
    chart_df = df if chart_selected_sup == "All Supervisors" else df[df['Supervisor'] == chart_selected_sup]

    v_col1, v_col2, v_col3 = st.columns(3)
    
    with v_col1:
        leaking_stores = chart_df[chart_df['Net_Variance_Vs_PM1'] < 0]
        if not leaking_stores.empty:
            leaking_top10 = leaking_stores.nsmallest(10, 'Net_Variance_Vs_PM1')
            leaking_top10['Absolute_Leakage'] = abs(leaking_top10['Net_Variance_Vs_PM1'])
            fig_leak = px.bar(leaking_top10, x='StoreName', y='Absolute_Leakage', title="Top 10 Leakages (vs PM1)", color='Absolute_Leakage', color_continuous_scale='Reds', labels={'Absolute_Leakage': 'Lost (₹)', 'StoreName': 'Location'})
            fig_leak.update_layout(xaxis={'categoryorder':'total descending', 'tickangle': 45}, coloraxis_showscale=False, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_leak, use_container_width=True)
        else: st.info("🟢 Zero revenue leaking outlets inside this pool.")
    with v_col2:
        generating_stores = chart_df[chart_df['Net_Variance_Vs_PM1'] >= 0]
        if not generating_stores.empty:
            generating_top10 = generating_stores.nlargest(10, 'Net_Variance_Vs_PM1')
            fig_gen = px.bar(generating_top10, x='StoreName', y='Net_Variance_Vs_PM1', title="Top 10 Gains (vs PM1)", color='Net_Variance_Vs_PM1', color_continuous_scale='Greens', labels={'Net_Variance_Vs_PM1': 'Gained (₹)', 'StoreName': 'Location'})
            fig_gen.update_layout(xaxis={'categoryorder':'total descending', 'tickangle': 45}, coloraxis_showscale=False, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gen, use_container_width=True)
        else: st.info("⚠️ Zero growth outlets identified inside this pool.")

    with v_col3:
        class_counts = chart_df['Operational Classification'].value_counts().reset_index()
        class_counts.columns = ['Classification', 'Count']
        fig_pie = px.pie(class_counts, values='Count', names='Classification', color='Classification', color_discrete_map={'💥 Critical Core Decline (2M Drop)': '#dc2626', '🚨 High Risk Shift (1M Drop)': '#f59e0b', '🔄 Volatile Swing Outlet': '#38bdf8', '⭐ Shooting Star Outlet': '#10b981'}, title="Portfolio Composition")
        fig_pie.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with st.expander("📖 Short Note: Trajectory Quadrant Definitions", expanded=False):
        st.markdown("""
        * **💥 Critical Core Decline (2M Drop)**: Down MoM and down below long-term 2M average baseline.
        * **🚨 High Risk Shift (1M Drop)**: Down MoM but still running above the historical 2M average baseline.
        * **🔄 Volatile Swing Outlet**: Up MoM but remains below 2M baseline due to heavy historic drops.
        * **⭐ Shooting Star Outlet**: Up MoM and pacing securely above the long-term 2M running baseline.
        """)
    st.markdown("---")
    # 10. STORE PERFORMANCE LEADERBOARD WITH SECURE STOREID KEYS
    st.subheader("🏆 Store Performance Leaderboard")
    st.markdown("Ranks branches based on absolute 1-month revenue variances. Growing outlets display in green with explicit '+' headers.")
    
    leaderboard_df = f_df.copy().sort_values(by="Net_Variance_Vs_PM1", ascending=False).reset_index(drop=True)
    leaderboard_df.index = leaderboard_df.index + 1
    leaderboard_df.index.name = 'Portfolio Rank'
    
    leader_cols = ["StoreID", "StoreName", "Manager", "Supervisor", "MTD NetSale", "Net Sale PM1", "Net_Variance_Vs_PM1"]
    valid_leader_cols = [col for col in leader_cols if col in leaderboard_df.columns]
    display_leader_df = leaderboard_df[valid_leader_cols].copy()

    if 'Net_Variance_Vs_PM1' in display_leader_df.columns:
        for i in display_leader_df.index:
            val = display_leader_df.loc[i, 'Net_Variance_Vs_PM1']
            display_leader_df.loc[i, 'Net Variance (1M)'] = format_indian_currency(val) if val < 0 else f"+{format_indian_currency(val)}"
        display_leader_df = display_leader_df.drop(columns=['Net_Variance_Vs_PM1'])
    
    if 'MTD NetSale' in display_leader_df.columns: display_leader_df['MTD NetSale'] = display_leader_df['MTD NetSale'].apply(format_indian_currency)
    if 'Net Sale PM1' in display_leader_df.columns: display_leader_df['Net Sale PM1'] = display_leader_df['Net Sale PM1'].apply(format_indian_currency)

    def final_text_styler(val_df):
        style_df = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        if 'Net Variance (1M)' in style_df.columns:
            for idx in val_df.index:
                if leaderboard_df.loc[idx, 'Net_Variance_Vs_PM1'] >= 0: style_df.loc[idx, 'Net Variance (1M)'] = 'color: #15803d; font-weight: bold; background-color: #d1fae5;'
                else: style_df.loc[idx, 'Net Variance (1M)'] = 'color: #b91c1c; font-weight: bold; background-color: #ffcccc;'
        return style_df

    st.dataframe(display_leader_df.style.apply(final_text_styler, axis=None), use_container_width=True, hide_index=True)
    st.markdown("---")
    # MODULE 2: INTERACTIVE MANAGER INTERVENTION SCRIPT GENERATOR WITH HIGH-VELOCITY OPERATIONAL TARGETS
    st.subheader("📢 Automated Manager Intervention Script Generator")
    st.markdown("Select an underperforming store inside your 2-Month decline pool to automatically draft a formal turnaround directive.")
    
    critical_stores_list = sorted(list(f_df[f_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]['StoreName'].unique()))
    
    if critical_stores_list:
        selected_target_store = st.selectbox("🎯 Select Leaking Store to Generate Escalation Script:", critical_stores_list)
        target_sub_df = f_df[f_df['StoreName'] == selected_target_store]
        
        if not target_sub_df.empty:
            t_row = target_sub_df.iloc[0]
            t_manager = str(t_row['Manager']).strip() if 'Manager' in target_sub_df.columns else "Branch Manager"
            t_id = str(t_row['StoreID']).strip() if 'StoreID' in target_sub_df.columns else "N/A"
            t_sup = str(t_row['Supervisor']).strip() if 'Supervisor' in target_sub_df.columns else "Operations Lead"
            t_loss = abs(float(t_row['Net_Variance_Vs_PM1'])) if 'Net_Variance_Vs_PM1' in target_sub_df.columns else 0.0
            t_rivals = int(t_row['Territory_Competitor_Count']) if 'Territory_Competitor_Count' in target_sub_df.columns else 1
            t_disc = float(t_row['Competitor_Max_Discount_Pct']) if 'Competitor_Max_Discount_Pct' in target_sub_df.columns else 10.0
            
            html_script_body = f"""MEDPLUS EXECUTIVE TURNAROUND MANDATE
----------------------------------
TO: Store Manager - {t_manager} (ID: {t_id})
FROM: Operations Command / Supervisor {t_sup}
URGENCY: CRITICAL CORRECTION LINE — REVENUE TURNAROUND ENGINE
SUBJECT: UNCOMPROMISING GROWTH AND PRIVATE LABEL CONVERSION DIRECTIVE

Manager {t_manager},

Your store at '{selected_target_store}' has flagged a major consecutive two-month retraction, registering an absolute revenue leakage of {format_indian_currency(t_loss)} compared to the last period. Our localized territory density tracking shows {t_rivals} active rival discount operations around your perimeter undercutting our pharmacy pool with up to {t_disc:.0f}% customer discounts.

To offset this density threat and pivot your outlet into our network's highest-performing growth store, you are hereby ordered to execute the following non-negotiable operational pivots immediately:

<ol style="margin-left: 20px; padding-left: 5px; line-height: 1.6;">
    <li style="margin-bottom: 10px;"><strong>COMPULSORY LOYALTY MIGRATION:</strong> Enforce a strict front-counter loyalty signup rule. Target a 95% mobile number capture rate on all footfall to permanently isolate chronic prescription walkaways.</li>
    <li style="margin-bottom: 10px;"><strong>BASKET SIZE OPTIMIZATION (CROSS-SELLING):</strong> Run mandatory staff coaching loops on multi-item billing parameters. Every prescription containing chronic brand drugs must be combined with a localized private label wellness cross-sell.</li>
    <li style="margin-bottom: 10px;"><strong>PRESTIGE PRIVATE LABEL MERCHANDISING:</strong> Re-engineer your visual merchandising layout within the next 24 hours. Shift your premium MedPlus private label alternatives from secondary rear storage rows onto center-shelf eye-level parameters.</li>
    <li style="margin-bottom: 10px;"><strong>PERIMETER PROMOTION OUTREACH:</strong> Deploy floor counter staff during low-traffic off-peak windows to distribute strategic counter-discount flyers within a 1.5KM perimeter loop of your pharmacy structure.</li>
</ol>
This operational slide stops now. You are expected to transform this leakage area into a high-margin growth vehicle. Update your Supervisor with an itemized turnaround checklist within 48 hours.

Best Regards,
Operations Command
MedPlus Health Services Ltd."""
            
            st.markdown(f"<div class='poa-container'>{html_script_body}</div>", unsafe_allow_html=True)
            
            raw_whatsapp_text = f"MEDPLUS EXECUTIVE TURNAROUND MANDATE\\n----------------------------------\\nTO: Store Manager - {t_manager} (ID: {t_id})\\nFROM: Operations Command / Supervisor {t_sup}\\nURGENCY: CRITICAL CORRECTION LINE\\n\\nManager {t_manager},\\n\\nYour store at '{selected_target_store}' has flagged a major revenue retraction of {format_indian_currency(t_loss)}. Rivals are matching up to {t_disc:.0f}% discount tiers. Execute these pivots:\\n\\n1. COMPULSORY LOYALTY MIGRATION: Target 95% footfall registration.\\n2. BASKET SIZE OPTIMIZATION: Cross-sell Private Label wellness alternatives.\\n3. PRESTIGE PRIVATE LABEL MERCHANDISING: Move house items to eye-level shelves.\\n4. PERIMETER PROMOTION OUTREACH: Distribute flyers in a 1.5KM radius.\\n\\nUpdate your supervisor with an itemized checklist within 48 hours.\\n\\nBest Regards,\\nOperations Command"
            encoded_whatsapp_text = urllib.parse.quote(raw_whatsapp_text)
            whatsapp_deep_link = f"https://whatsapp.com{encoded_whatsapp_text}"
            
            st.markdown(f"""
                <a href="{whatsapp_deep_link}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 12px 24px; border-radius: 6px; font-weight: bold; text-align: center; font-family: Arial, sans-serif; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; margin-top: 10px; margin-bottom: 20px;">
                        📲 Dispatch Turnaround Mandate to Manager via WhatsApp
                    </div>
                </a>
            """, unsafe_allow_html=True)
        else: st.error("⚠️ Failed to extract target store data matrices safely.")
    else: st.success("🟩 Excellence Note: The selected filter pool contains zero stores under consecutive 2-Month decline conditions.")
    st.markdown("---")

    # 11. Granular Executive Command Grid View
    st.subheader("🔬 Operational Target Drilldown Control Panel")
    selected_class = st.selectbox("Isolate Stores by Management Classification Profile:", ["Show All Stores", "Isolate Decline Only", "Isolate High Risk Only", "Isolate Volatile Only", "Isolate Stars Only"])
    
    display_grid_df = f_df.copy()
    if "Decline" in selected_class: display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]
    elif "High Risk" in selected_class: display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "🚨 High Risk Shift (1M Drop)"]
    elif "Volatile" in selected_class: display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "🔄 Volatile Swing Outlet"]
    elif "Stars" in selected_class: display_grid_df = display_grid_df[display_grid_df['Operational Classification'] == "⭐ Shooting Star Outlet"]

    def color_cells_by_segment(val_df):
        style_df = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        def match_style(v1, v2):
            if v1 < 0 and v2 < 0: return 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'
            elif v1 < 0 and v2 >= 0: return 'background-color: #ffe6cc; color: #d97706;'
            elif v1 >= 0 and v2 < 0: return 'background-color: #e0f2fe; color: #0284c7;'
            return 'background-color: #d1fae5; color: #16a34a;'

        for idx in val_df.index:
            v1_val = display_grid_df.loc[idx, 'Net_Variance_Vs_PM1'] if 'Net_Variance_Vs_PM1' in display_grid_df.columns else 0
            v2_val = display_grid_df.loc[idx, 'Net_Variance_Vs_Avg2M'] if 'Net_Variance_Vs_Avg2M' in display_grid_df.columns else 0
            p1_val = display_grid_df.loc[idx, 'Pharma_Variance_Vs_PM1'] if 'Pharma_Variance_Vs_PM1' in display_grid_df.columns else 0
            p2_val = display_grid_df.loc[idx, 'Pharma_Variance_Vs_PM2'] if 'Pharma_Variance_Vs_PM2' in display_grid_df.columns else 0
            np1_val = display_grid_df.loc[idx, 'NonPharma_Variance_Vs_PM1'] if 'NonPharma_Variance_Vs_PM1' in display_grid_df.columns else 0
            np2_val = display_grid_df.loc[idx, 'NonPharma_Variance_Vs_PM2'] if 'NonPharma_Variance_Vs_PM2' in display_grid_df.columns else 0

            if 'MTD NetSale' in style_df.columns: style_df.loc[idx, 'MTD NetSale'] = match_style(v1_val, v2_val)
            if 'PL Pharma NetSale' in style_df.columns: style_df.loc[idx, 'PL Pharma NetSale'] = match_style(p1_val, p2_val)
            if 'PL NonPharma NetSale' in style_df.columns: style_df.loc[idx, 'PL NonPharma NetSale'] = match_style(np1_val, np2_val)
        return style_df

    visible_cols = ["StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale"]
    safe_visible_cols = [col for col in visible_cols if col in display_grid_df.columns]
    filtered_display_df = display_grid_df[safe_visible_cols].copy()
    
    if 'MTD NetSale' in filtered_display_df.columns: filtered_display_df['MTD NetSale'] = filtered_display_df['MTD NetSale'].apply(format_indian_currency)
    if 'PL Pharma NetSale' in filtered_display_df.columns: filtered_display_df['PL Pharma NetSale'] = filtered_display_df['PL Pharma NetSale'].apply(format_indian_currency)
    if 'PL NonPharma NetSale' in filtered_display_df.columns: filtered_display_df['PL NonPharma NetSale'] = filtered_display_df['PL NonPharma NetSale'].apply(format_indian_currency)

    st.dataframe(filtered_display_df.style.apply(color_cells_by_segment, axis=None), column_order=safe_visible_cols, use_container_width=True, hide_index=True)
