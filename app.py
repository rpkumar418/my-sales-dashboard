import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Multi-Month Sales Decline Analysis", layout="wide")
st.title("📉 Multi-Month Performance Decline Dashboard")
st.markdown("This control center monitors consecutive month-over-month trends (**Current MTD vs PM1 vs PM2**) to identify sustained portfolio risks at the Supervisor level.")

# 2. Data Cleaning and Transformation Engine
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
        
        # Prune total row lines
        if 'S. No.' in df.columns:
            df = df[df['S. No.'].astype(str).str.lower().str.strip() != 'total']
        if 'StoreName' in df.columns:
            df = df[df['StoreName'].dropna().str.lower().str.strip() != 'total']
            
        def clean_numeric(val):
            if pd.isna(val):
                return 0.0
            val_str = str(val).replace('"', '').replace(',', '').strip()
            return pd.to_numeric(val_str, errors='coerce') if val_str else 0.0

        # Include PM2 performance tracking matrices into the parsing loop
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
        st.error(f"Error compiling ledger: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⚠️ Dataset empty or corrupted. Verify filename on GitHub.")
else:
    # 3. Compute Month-over-Month Variances
    # Current month vs 1 Month Ago (PM1)
    df['Net_Var_PM1'] = df['MTD NetSale'] - df['Net Sale PM1']
    df['Pharma_Var_PM1'] = df['PL Pharma NetSale'] - df['Pharma PM1']
    df['NonPharma_Var_PM1'] = df['PL NonPharma NetSale'] - df['NON Pharma PM1']

    # 1 Month Ago (PM1) vs 2 Months Ago (PM2)
    df['Net_Var_PM2'] = df['Net Sale PM1'] - df['Net Sale PM2']
    df['Pharma_Var_PM2'] = df['Pharma PM1'] - df['Pharma PM2']
    df['NonPharma_Var_PM2'] = df['NON Pharma PM1'] - df['NON Pharma PM2']

    # 4. Flags for Consecutive 2-Month Multi-Month Decline
    df['Net_Multi_Decline'] = (df['Net_Var_PM1'] < 0) & (df['Net_Var_PM2'] < 0)
    df['Pharma_Multi_Decline'] = (df['Pharma_Var_PM1'] < 0) & (df['Pharma_Var_PM2'] < 0)
    df['NonPharma_Multi_Decline'] = (df['NonPharma_Var_PM1'] < 0) & (df['NonPharma_Var_PM2'] < 0)

    # 5. Core Executive Health Scorecards
    st.subheader("🚨 Sustained Risk Critical Flags")
    tot_stores = len(df)
    tot_net_streak = df['Net_Multi_Decline'].sum()
    tot_pharma_streak = df['Pharma_Multi_Decline'].sum()
    tot_nonpharma_streak = df['NonPharma_Multi_Decline'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🏬 Network Footprint", value=f"{tot_stores} Total Stores")
    with col2:
        st.metric(label="⚠️ Net Revenue Decline Streak", value=f"{tot_net_streak} Outlets", delta="Sustained Drop", delta_color="inverse")
    with col3:
        st.metric(label="⚠️ Pharma Decline Streak", value=f"{tot_pharma_streak} Outlets", delta="Sustained Drop", delta_color="inverse")
    with col4:
        st.metric(label="⚠️ Non-Pharma Decline Streak", value=f"{tot_nonpharma_streak} Outlets", delta="Sustained Drop", delta_color="inverse")

    st.markdown("---")

    # 6. Supervisor Risk Portfolio Ledger Block
    st.subheader("📋 Supervisor Portfolio Multi-Month Risk Matrix")
    st.markdown("Review which supervisors have the highest concentration of outlets showing multi-month performance declines.")

    supervisor_summary = df.groupby('Supervisor').agg(
        Total_Assigned_Stores=('StoreID', 'nunique'),
        Net_De_growth_PM1=('Net_Var_PM1', lambda x: (x < 0).sum()),
        Sustained_Net_Decline=('Net_Multi_Decline', 'sum'),
        Sustained_Pharma_Decline=('Pharma_Multi_Decline', 'sum'),
        Sustained_NonPharma_Decline=('NonPharma_Multi_Decline', 'sum'),
        Current_MTD_Net_Sales=('MTD NetSale', 'sum')
    ).reset_index()

    # Re-label columns cleanly for executives
    display_summary = supervisor_summary.copy()
    display_summary.columns = [
        "Supervisor Name", "Total Stores", "Stores down this month (vs PM1)",
        "🔥 Critical Net Sale Streak Drop", "🚨 Sustained Pharma Decline", "🛍️ Sustained Non-Pharma Decline", "Current Net Value (₹)"
    ]

    st.dataframe(
        display_summary.style.format({
            "Current Net Value (₹)": "₹{:,.2f}"
        }).background_gradient(subset=["🔥 Critical Net Sale Streak Drop"], cmap="Oranges"),
        use_container_width=True
    )

    st.markdown("---")

    # 7. Multi-Month Trend Visualization Chart
    st.subheader("📊 Volumetric Breakdown of Long-Term Decline Risks")
    
    melted_trends = pd.melt(
        supervisor_summary,
        id_vars=['Supervisor'],
        value_vars=['Sustained_Net_Decline', 'Sustained_Pharma_Decline', 'Sustained_NonPharma_Decline'],
        var_name='Risk Category',
        value_name='Count of Stores'
    )
    melted_trends['Risk Category'] = melted_trends['Risk Category'].map({
        'Sustained_Net_Decline': 'Net Sales Drop (2+ Months)',
        'Sustained_Pharma_Decline': 'Pharma PL Drop (2+ Months)',
        'Sustained_NonPharma_Decline': 'Non-Pharma PL Drop (2+ Months)'
    })

    fig_trends = px.bar(
        melted_trends,
        x="Supervisor",
        y="Count of Stores",
        color="Risk Category",
        barmode="group",
        title="Portfolio Volume experiencing Multi-Month Decline Stretches",
        color_discrete_sequence=px.colors.sequential.Flame_r
    )
    st.plotly_chart(fig_trends, use_container_width=True)

    st.markdown("---")

    # 8. Filtered Risk Action List Finder
    st.subheader("🔍 Critical Multi-Month Risk Outlet Finder")
    
    risk_filter = st.radio("Isolate Stores by Risk Status:", ["Show Stores with Sustained Net Sales Drop", "Show Entire Network Data Profile"])
    
    drilldown_cols = [
        "StoreName", "Supervisor", "Manager", "MTD NetSale", "Net Sale PM1", "Net Sale PM2",
        "PL Pharma NetSale", "Pharma PM1", "Pharma PM2",
        "PL NonPharma NetSale", "NON Pharma PM1", "NON Pharma PM2"
    ]
    
    if "Sustained Net Sales Drop" in risk_filter:
        action_df = df[df['Net_Multi_Decline'] == True]
    else:
        action_df = df

    st.dataframe(action_df[drilldown_cols].sort_values(by="MTD NetSale"), use_container_width=True)

except Exception as e:
    st.error(f"Application Runtime Error: {e}")
