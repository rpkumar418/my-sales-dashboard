import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re

st.set_page_config(page_title="MedPlus Turnaround Command", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 23px !important; font-weight: 700 !important; color: #1e293b !important; }
    [data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 600 !important; color: #475569 !important; }
    .custom-subtext { font-size: 11px; color: #64748b; margin-top: -8px; margin-bottom: 12px; font-weight: 500; }
    .poa-container { background-color: #fef2f2; border: 1px solid #fee2e2; padding: 15px; border-radius: 8px; color: #991b1b; font-family: monospace; white-space: pre-wrap; }
    
    /* Elegant Inline Branding Flexbox Matrix */
    .brand-header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .medplus-logo-box { 
        background-color: #e11d48; 
        color: #ffffff; 
        font-family: Arial, sans-serif; 
        font-size: 32px; 
        font-weight: 800; 
        padding: 6px 22px; 
        border-radius: 6px; 
        display: inline-block; 
        letter-spacing: -1px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); 
    }
    .medplus-plus-sign { color: #22c55e; font-weight: 900; margin-left: 2px; }
    .title-text-box h1 {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 34px !important;
        color: #0f172a !important;
    }
    .title-text-box h5 {
        margin: 4px 0 0 0 !important;
        padding: 0 !important;
        color: #64748b !important;
    }
    </style>
""", unsafe_allow_html=True)

# FIXED: Re-engineered inline flex layout to prevent header collapsing issues
st.markdown("""
    <div class="brand-header-container">
        <div class="medplus-logo-box">MedPlus<span class="medplus-plus-sign">+</span></div>
        <div class="title-text-box">
            <h1>Supervisor Performance Dashboard</h1>
            <h5>Enterprise Margin Optimization & Turnaround Engine</h5>
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

def format_indian_currency(number):
    try:
        is_negative = number < 0
        abs_num = abs(number)
        s = f"{abs_num:.2f}"
        parts = s.split('.')
        num_part = parts[0]
        dec_part = parts[1]
        if len(num_part) <= 3:
            res = num_part
        else:
            last_three = num_part[-3:]
            remaining = num_part[:-3]
            remaining_rev = remaining[::-1]
            groups = [remaining_rev[i:i+2] for i in range(0, len(remaining_rev), 2)]
            res = f"{','.join(groups)[::-1]},{last_three}"
        return f"₹{'-' if is_negative else ''}{res}.{dec_part}"
    except:
        return f"₹{number:,.2f}"
@st.cache_data
def load_data():
    days = 30
    try:
        with open("sales_data.csv", "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
        m = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', first_line)
        if m: days = max(1, min(31, int(m.group(1))))
    except: pass
    try:
        with open("sales_data.csv", "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        h_idx = 0
        for i, line in enumerate(lines):
            if "StoreName" in line or "StoreID" in line:
                h_idx = i
                break
        df = pd.read_csv("sales_data.csv", skiprows=h_idx)
        df.columns = [str(col).strip() for col in df.columns if str(col).strip()]
        if 'S. No.' in df.columns: df = df[df['S. No.'].astype(str).str.lower().str.strip() != 'total']
        if 'StoreName' in df.columns: df = df[df['StoreName'].dropna().str.lower().str.strip() != 'total']
        
        def clean_num(v):
            if pd.isna(v): return 0.0
            s = str(v).replace('"', '').replace(',', '').strip()
            return pd.to_numeric(s, errors='coerce') if s else 0.0

        for col in ['MTD NetSale', 'PL Pharma NetSale', 'PL NonPharma NetSale', 'Net Sale PM1', 'Pharma PM1', 'NON Pharma PM1', 'Net Sale PM2', 'Pharma PM2', 'NON Pharma PM2']:
            if col in df.columns: df[col] = df[col].apply(clean_num).fillna(0.0)
            else: df[col] = 0.0
        return df, days
    except Exception as e:
        st.error(f"Intake Failure: {e}")
        return pd.DataFrame(), days

df, mtd_days_elapsed = load_data()

if df.empty:
    st.warning("⚠️ Critical: 'sales_data.csv' missing from workspace.")
else:
    df['Net_Variance_Vs_PM1'] = df['MTD NetSale'] - df['Net Sale PM1']
    df['Net_Variance_Vs_PM2'] = df['Net Sale PM1'] - df['Net Sale PM2']
    df['Net_Variance_Vs_Avg2M'] = df['MTD NetSale'] - ((df['Net Sale PM1'] + df['Net Sale PM2']) / 2)
    df['Pharma_Variance_Vs_PM1'] = df['PL Pharma NetSale'] - df['Pharma PM1']
    df['Pharma_Variance_Vs_PM2'] = df['Pharma PM1'] - df['Pharma PM2']
    df['NonPharma_Variance_Vs_PM1'] = df['PL NonPharma NetSale'] - df['NON Pharma PM1']
    df['NonPharma_Variance_Vs_PM2'] = df['NON Pharma PM1'] - df['NON Pharma PM2']
    
    df['Territory_Competitor_Count'] = df['StoreID'].apply(lambda x: (sum(ord(c) for c in str(x)) % 5) + 1)
    df['Competitor_Max_Discount_Pct'] = df['StoreID'].apply(lambda x: 10.0 + (sum(ord(c) for c in str(x)) % 11))

    def get_class(r):
        if r['Net_Variance_Vs_PM1'] < 0 and r['Net_Variance_Vs_Avg2M'] < 0: return "💥 Critical Core Decline (2M Drop)"
        if r['Net_Variance_Vs_PM1'] < 0 and r['Net_Variance_Vs_Avg2M'] >= 0: return "🚨 High Risk Shift (1M Drop)"
        if r['Net_Variance_Vs_PM1'] >= 0 and r['Net_Variance_Vs_Avg2M'] < 0: return "🔄 Volatile Swing Outlet"
        return "⭐ Shooting Star Outlet"
    df['Operational Classification'] = df.apply(get_class, axis=1)
    st.subheader("📥 Master Operational Data Hub")
    master_buffer = io.BytesIO()
    with pd.ExcelWriter(master_buffer, engine='xlsxwriter') as writer:
        export_cols = ["StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", "Net Sale PM1", "Net Sale PM2", "PL Pharma NetSale", "PL NonPharma NetSale", "Net_Variance_Vs_PM1", "Operational Classification"]
        valid_cols = [col for col in export_cols if col in df.columns]
        df[valid_cols].sort_values(by="Net_Variance_Vs_PM1", ascending=True).to_excel(writer, sheet_name="MasterRegistry", index=False)
    st.download_button("📥 Download Master Operations & POA Report (.xlsx)", master_buffer.getvalue(), "Master_Operations_Turnaround_Registry.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("---")

    st.subheader("📌 Corporate Network Financial Health Command")
    st.info(f"📆 Temporal Context Engine Auto-Detected: **{mtd_days_elapsed} Days Elapsed**")
    unique_sups = ["All Supervisors"] + sorted(list(df['Supervisor'].dropna().unique()))
    selected_sup = st.selectbox("🎯 Select District Supervisor Portfolio to Audit", unique_sups)
    f_df = df if selected_sup == "All Supervisors" else df[df['Supervisor'] == selected_sup]
    
    tot_sales = f_df['MTD NetSale'].sum()
    ph_pct = (f_df['PL Pharma NetSale'].sum() / tot_sales * 100) if tot_sales > 0 else 0.0
    np_pct = (f_df['PL NonPharma NetSale'].sum() / tot_sales * 100) if tot_sales > 0 else 0.0
    
    # FIXED: Re-mapped metric names defensively to completely erase the line 145 NameError
    pm1_sales = f_df['Net Sale PM1'].sum()
    pm1_ph_pct = (f_df['Pharma PM1'].sum() / pm1_sales * 100) if pm1_sales > 0 else 0.0
    pm1_np_pct = (f_df['NON Pharma PM1'].sum() / pm1_sales * 100) if pm1_sales > 0 else 0.0
    
    pm2_sales = f_df['Net Sale PM2'].sum()
    pm2_ph_pct = (f_df['Pharma PM2'].sum() / pm2_sales * 100) if pm2_sales > 0 else 0.0
    pm2_np_pct = (f_df['NON Pharma PM2'].sum() / pm2_sales * 100) if pm2_sales > 0 else 0.0
    
    s_diff_1m = tot_sales - pm1_sales
    s_diff_2m = tot_sales - ((pm1_sales + pm2_sales) / 2)
    num_stores = max(1, len(f_df))
    
    st.markdown(f"#### 📊 Performance Ledger Overview for: **{selected_sup}**")
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    r1_c1.metric("💼 Total Network Gross Sales (Current)", format_indian_currency(tot_sales))
    r1_c1.markdown(f"<div class='custom-subtext'>▲ Daily Store Avg: {format_indian_currency(tot_sales/num_stores/mtd_days_elapsed)}</div>", unsafe_allow_html=True)
    r1_c2.metric("💊 Pharma % (Current)", f"{ph_pct:.2f}%")
    r1_c2.markdown("<div class='custom-subtext'>Target Mix: 35.00%</div>", unsafe_allow_html=True)
    r1_c3.metric("🛍️ Non-Pharma % (Current)", f"{np_pct:.2f}%")
    r1_c3.markdown("<div class='custom-subtext'>Target Mix: 65.00%</div>", unsafe_allow_html=True)
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    r2_c1.metric("🗓️ PM1 Network Gross Sales", format_indian_currency(pm1_sales))
    r2_c1.markdown(f"<div class='custom-subtext'>▼ Daily Store Avg: {format_indian_currency(pm1_sales/num_stores/mtd_days_elapsed)}</div>", unsafe_allow_html=True)
    r2_c2.metric("💊 PM1 Pharma %", f"{pm1_ph_pct:.2f}%")
    r2_c2.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    r2_c3.metric("🛍️ PM1 Non-Pharma %", f"{pm1_np_pct:.2f}%")
    r2_c3.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    
    r3_c1, r3_c2, r3_c3 = st.columns(3)
    r3_c1.metric("🗓️ PM2 Network Gross Sales", format_indian_currency(pm2_sales))
    r3_c1.markdown(f"<div class='custom-subtext'>▼ Daily Store Avg: {format_indian_currency(pm2_sales/num_stores/mtd_days_elapsed)}</div>", unsafe_allow_html=True)
    r3_c2.metric("💊 PM2 Pharma %", f"{pm2_ph_pct:.2f}%")
    r3_c2.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    r3_c3.metric("🛍️ PM2 Non-Pharma %", f"{pm2_np_pct:.2f}%")
    r3_c3.markdown("<div class='custom-subtext'>Historical Baseline</div>", unsafe_allow_html=True)
    
    st.markdown("##### 📈 Growth & Trajectory Tracking Variances")
    r4_c1, r4_c2, r4_c3, r4_c4 = st.columns(4)
    r4_c1.metric("🔄 1-Month Sales Diff", format_indian_currency(s_diff_1m))
    r4_c1.markdown(f"<div class='custom-subtext'>Daily Store Avg: {'▲' if s_diff_1m>=0 else '▼'} {format_indian_currency(abs(s_diff_1m/num_stores/mtd_days_elapsed))}</div>", unsafe_allow_html=True)
    r4_c2.metric("📉 2-Month Avg Sales Diff", format_indian_currency(s_diff_2m))
    r4_c2.markdown(f"<div class='custom-subtext'>Daily Store Avg: {'▲' if s_diff_2m>=0 else '▼'} {format_indian_currency(abs(s_diff_2m/num_stores/mtd_days_elapsed))}</div>", unsafe_allow_html=True)
    r4_c3.metric("💊 Pharma % Diff (1M)", f"{ph_pct-pm1_ph_pct:+.2f}%")
    r4_c3.markdown(f"<div class='custom-subtext'>Mix Shift: {'▲' if ph_pct>=pm1_ph_pct else '▼'} {abs(ph_pct-pm1_ph_pct):.2f}%</div>", unsafe_allow_html=True)
    r4_c4.metric("🛍️ Non-Pharma % Diff (1M)", f"{np_pct-pm1_np_pct:+.2f}%")
    r4_c4.markdown(f"<div class='custom-subtext'>Mix Shift: {'▲' if np_pct>=pm1_np_pct else '▼'} {abs(np_pct-pm1_np_pct):.2f}%</div>", unsafe_allow_html=True)
    
    st.markdown("##### 💰 Dynamic Tier-2 Financial Velocity Tracking Matrix")
    t2_col1, t2_col2, t2_col3, t2_col4 = st.columns(4)
    m1_g = f_df[f_df['Net_Variance_Vs_PM1'] >= 0]['Net_Variance_Vs_PM1'].sum()
    m1_d = f_df[f_df['Net_Variance_Vs_PM1'] < 0]['Net_Variance_Vs_PM1'].sum()
    m2_g = f_df[f_df['Net_Variance_Vs_Avg2M'] >= 0]['Net_Variance_Vs_Avg2M'].sum()
    m2_d = f_df[f_df['Net_Variance_Vs_Avg2M'] < 0]['Net_Variance_Vs_Avg2M'].sum()
    
    t2_col1.markdown(f"<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟩 1M Growth Value</p><p style='font-size:18px; color:#16a34a; font-weight:700; margin:0;'>{format_indian_currency(m1_g)}</p>", unsafe_allow_html=True)
    t2_col2.markdown(f"<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟧 1M Degrowth Value</p><p style='font-size:18px; color:#ea580c; font-weight:700; margin:0;'>{format_indian_currency(m1_d)}</p>", unsafe_allow_html=True)
    t2_col3.markdown(f"<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟩 2M Growth Value</p><p style='font-size:18px; color:#16a34a; font-weight:700; margin:0;'>{format_indian_currency(m2_g)}</p>", unsafe_allow_html=True)
    t2_col4.markdown(f"<p style='font-size:13px; color:#475569; font-weight:600; margin-bottom:2px;'>🟥 2M Degrowth Value</p><p style='font-size:18px; color:#dc2626; font-weight:700; margin:0;'>{format_indian_currency(m2_d)}</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("🔮 Predictive Private Label Optimization Sandbox")
    sim_col1, sim_col2 = st.columns(2)
    b_ph = sim_col1.slider("Brand Pharma Margin (%)", 10, 25, 15) / 100.0
    l_ph = sim_col1.slider("PL Pharma Margin (%)", 30, 55, 42) / 100.0
    ph_boost = sim_col2.slider("Target Pharma Share Shift to PL (%)", 0, 30, 5) / 100.0
    c_pl_ph = f_df['PL Pharma NetSale'].sum()
    t_ph_pool = c_pl_ph * 3.5
    c_br_ph = max(0.0, t_ph_pool - c_pl_ph)
    b_prof = (c_br_ph * b_ph) + (c_pl_ph * l_ph)
    m_ph = c_br_ph * ph_boost
    s_prof = ((c_br_ph - m_ph) * b_ph) + ((c_pl_ph + m_ph) * l_ph)
    sim_col2.metric("📈 Simulated Profit Expansion", format_indian_currency(s_prof - b_prof))
    st.markdown("---")
    st.subheader("📋 Supervisor Portfolio Summary")
    with st.expander("📝 Short Note: Audit Guidelines", expanded=False):
        st.markdown("* **Accounting Match**: Total Stores = 1M Degrowth + 1M Growth = 2M Degrowth + 2M Growth.\n* **1M vs 2M**: 1M evaluates vs last month (PM1); 2M vs two-month historic average matrix.\n* **Review Target**: Audit portfolios with severe red backgrounds under **2M Degrowth Value**.")
        
    s_matrix = []
    for s_name, s_data in df.groupby('Supervisor'):
        s_matrix.append({
            "Supervisor Name": s_name, "Total Stores": s_data['StoreID'].nunique(), "CM Net Sales": s_data['MTD NetSale'].sum(),
            "🏆 Territory Growth Index": ((s_data['MTD NetSale'].sum() - s_data['Net Sale PM1'].sum()) / s_data['Net Sale PM1'].sum() * 100) if s_data['Net Sale PM1'].sum() > 0 else 0.0,
            "1M Degrowth Count": (s_data['Net_Variance_Vs_PM1'] < 0).sum(), "2M Degrowth Count": (s_data['Net_Variance_Vs_Avg2M'] < 0).sum(),
            "1M Degrowth Value": s_data[s_data['Net_Variance_Vs_PM1'] < 0]['Net_Variance_Vs_PM1'].sum(), "2M Degrowth Value": s_data[s_data['Net_Variance_Vs_Avg2M'] < 0]['Net_Variance_Vs_Avg2M'].sum()
        })
    s_sum_df = pd.DataFrame(s_matrix).sort_values(by="2M Degrowth Count", ascending=False)
    s_sum_df['CM Net Sales'] = s_sum_df['CM Net Sales'].apply(format_indian_currency)
    s_sum_df['1M Degrowth Value'] = s_sum_df['1M Degrowth Value'].apply(format_indian_currency)
    s_sum_df['2M Degrowth Value'] = s_sum_df['2M Degrowth Value'].apply(format_indian_currency)
    st.dataframe(s_sum_df.style.apply(lambda x: pd.DataFrame({'1M Degrowth Value': 'background-color: #ffe6cc; color: #d97706; font-weight: bold;', '2M Degrowth Value': 'background-color: #ffcccc; color: #cc0000; font-weight: bold;'}, index=x.index, columns=x.columns).fillna(''), axis=None).format({"🏆 Territory Growth Index": "{:+.2f}%"}), use_container_width=True, hide_index=True)
    st.markdown("---")

    st.header("📈 Strategic Visual Performance Framework")
    v_sups = ["All Supervisors"] + sorted(list(df['Supervisor'].dropna().unique()))
    c_sel_sup = st.selectbox("🔍 Filter Visual Framework Charts by Supervisor:", v_sups, key="vf_filter")
    c_df = df if c_sel_sup == "All Supervisors" else df[df['Supervisor'] == c_sel_sup]
    
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        st.subheader("📉 Top 10 Leakages")
        lk = c_df[c_df['Net_Variance_Vs_PM1'] < 0]
        if not lk.empty:
            st.plotly_chart(px.bar(lk.nsmallest(10, 'Net_Variance_Vs_PM1'), x='StoreName', y='Net_Variance_Vs_PM1', color='Net_Variance_Vs_PM1', color_continuous_scale='Reds', labels={'Net_Variance_Vs_PM1':'Lost'}).update_layout(xaxis={'tickangle': 45}, coloraxis_showscale=False, margin=dict(l=5,r=5,t=20,b=5)), use_container_width=True)
        else: st.info("🟢 Zero leakages found.")
    with v_col2:
        st.subheader("📈 Top 10 Gains")
        gn = c_df[c_df['Net_Variance_Vs_PM1'] >= 0]
        if not gn.empty:
            st.plotly_chart(px.bar(gn.nlargest(10, 'Net_Variance_Vs_PM1'), x='StoreName', y='Net_Variance_Vs_PM1', color='Net_Variance_Vs_PM1', color_continuous_scale='Greens', labels={'Net_Variance_Vs_PM1':'Gained'}).update_layout(xaxis={'tickangle': 45}, coloraxis_showscale=False, margin=dict(l=5,r=5,t=20,b=5)), use_container_width=True)
        else: st.info("⚠️ Zero growth outlets found.")
    with v_col3:
        st.subheader("📊 Portfolio Split")
        st.plotly_chart(px.pie(c_df['Operational Classification'].value_counts().reset_index(), values='count', names='Operational Classification', color='Operational Classification', color_discrete_map={'💥 Critical Core Decline (2M Drop)': '#dc2626', '🚨 High Risk Shift (1M Drop)': '#f59e0b', '🔄 Volatile Swing Outlet': '#38bdf8', '⭐ Shooting Star Outlet': '#10b981'}), use_container_width=True)
    with st.expander("📖 Short Note: Trajectory Quadrant Definitions", expanded=False):
        st.markdown("""* **💥 Critical Decline**: Down MoM and down below long-term 2M average baseline.\n* **🚨 High Risk Shift**: Down MoM but still running above the historical 2M average baseline.\n* **🔄 Volatile Swing**: Up MoM but remains below 2M baseline due to heavy historic drops.\n* **⭐ Shooting Star**: Up MoM and pacing securely above the long-term 2M running baseline.""")
    st.markdown("---")

    st.subheader("🏆 Store Performance Leaderboard")
    ld_df = f_df.copy().sort_values(by="Net_Variance_Vs_PM1", ascending=False).reset_index(drop=True)
    ld_df.index = ld_df.index + 1
    v_lead_cols = [c for c in ["StoreID", "StoreName", "Manager", "Supervisor", "MTD NetSale", "Net Sale PM1"] if c in ld_df.columns]
    disp_ld = ld_df[v_lead_cols].copy()
    for i in disp_ld.index: disp_ld.loc[i, 'Net Variance (1M)'] = format_indian_currency(ld_df.loc[i, 'Net_Variance_Vs_PM1'])
    disp_ld['MTD NetSale'] = disp_ld['MTD NetSale'].apply(format_indian_currency)
    disp_ld['Net Sale PM1'] = disp_ld['Net Sale PM1'].apply(format_indian_currency)
    st.dataframe(disp_ld.style.apply(lambda x: pd.DataFrame({'Net Variance (1M)': [ 'color: #15803d; font-weight: bold; background-color: #d1fae5;' if ld_df.loc[idx, 'Net_Variance_Vs_PM1'] >= 0 else 'color: #b91c1c; font-weight: bold; background-color: #ffcccc;' for idx in x.index ]}, index=x.index, columns=x.columns).fillna(''), axis=None), use_container_width=True, hide_index=True)
    st.markdown("---")

    st.subheader("📢 Automated Manager Intervention Script Generator")
    crit_list = sorted(list(f_df[f_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]['StoreName'].unique()))
    if crit_list:
        sel_store = st.selectbox("🎯 Select Leaking Store to Generate Escalation Script:", crit_list)
        t_row = f_df[f_df['StoreName'] == sel_store].iloc[0]
        script = f"MEDPLUS PERFORMANCE NOTICE\nTO: Store Manager - {t_row.get('Manager','Manager')} (ID: {t_row.get('StoreID','N/A')})\nFROM: Operations Command\nURGENCY: CRITICAL MANDATE - 2-MONTH LEAKAGE ISOLATION\n\nYour outlet at '{sel_store}' has flagged a major revenue retraction of {format_indian_currency(abs(t_row.get('Net_Variance_Vs_PM1',0)))} compared to last period. This consecutive multi-month slide requires immediate localized correction lines.\n\nUpdate operations turnaround logs within 48 hours.\n\nBest Regards,\nOperations Command\nMedPlus Health Services Ltd."
        st.markdown(f"<div class='poa-container'>{script}</div>", unsafe_allow_html=True)
    else: st.success("🟩 Excellence Note: Zero stores under consecutive 2-Month decline conditions.")
    st.markdown("---")

    st.subheader("🔬 Operational Target Drilldown Control Panel")
    sel_class = st.selectbox("Isolate Stores by Profile:", ["Show All Stores", "Isolate Decline Only", "Isolate High Risk Only", "Isolate Volatile Only", "Isolate Stars Only"])
    grid_df = f_df.copy()
    if "Decline" in sel_class: grid_df = grid_df[grid_df['Operational Classification'] == "💥 Critical Core Decline (2M Drop)"]
    elif "High Risk" in sel_class: grid_df = grid_df[grid_df['Operational Classification'] == "🚨 High Risk Shift (1M Drop)"]
    elif "Volatile" in sel_class: grid_df = grid_df[grid_df['Operational Classification'] == "🔄 Volatile Swing Outlet"]
    elif "Stars" in sel_class: grid_df = grid_df[grid_df['Operational Classification'] == "⭐ Shooting Star Outlet"]

    v_grid_cols = ["StoreID", "StoreName", "Supervisor", "Manager", "MTD NetSale", "PL Pharma NetSale", "PL NonPharma NetSale"]
    safe_grid_cols = [col for col in v_grid_cols if col in grid_df.columns]
    f_grid = grid_df[safe_grid_cols].copy()
    
    def color_grid(x):
        s_df = pd.DataFrame('', index=x.index, columns=x.columns)
        for idx in x.index:
            v1 = grid_df.loc[idx, 'Net_Variance_Vs_PM1'] if 'Net_Variance_Vs_PM1' in grid_df.columns else 0
            v2 = grid_df.loc[idx, 'Net_Variance_Vs_Avg2M'] if 'Net_Variance_Vs_Avg2M' in grid_df.columns else 0
            match = 'background-color: #ffcccc; color: #cc0000; font-weight: bold;' if (v1<0 and v2<0) else ('background-color: #ffe6cc; color: #d97706;' if (v1<0 and v2>=0) else ('background-color: #e0f2fe; color: #0284c7;' if (v1>=0 and v2<0) else 'background-color: #d1fae5; color: #16a34a;'))
            if 'MTD NetSale' in s_df.columns: s_df.loc[idx, 'MTD NetSale'] = match
        return s_df

    if 'MTD NetSale' in f_grid.columns: f_grid['MTD NetSale'] = f_grid['MTD NetSale'].apply(format_indian_currency)
    if 'PL Pharma NetSale' in f_grid.columns: f_grid['PL Pharma NetSale'] = f_grid['PL Pharma NetSale'].apply(format_indian_currency)
    if 'PL NonPharma NetSale' in f_grid.columns: f_grid['PL NonPharma NetSale'] = f_grid['PL NonPharma NetSale'].apply(format_indian_currency)
    st.dataframe(f_grid.style.apply(color_grid, axis=None), column_order=safe_grid_cols, use_container_width=True, hide_index=True)
