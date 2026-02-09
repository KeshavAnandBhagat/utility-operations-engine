import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Connect to your Database (Adjust URL to match models.py)
DB_URL = "sqlite:///billing_system.db" 
engine = create_engine(DB_URL)

st.set_page_config(page_title="Utility Admin Command Center", layout="wide")

st.title("⚡ Utility Executive Dashboard")

# --- Kpi Metric 1: Financials ---
st.header("1. Financial Overview (Jan 2026)")
try:
    # Fetch Data using Pandas (SQL Magic)
    query = "SELECT * FROM bills"
    df_bills = pd.read_sql(query, engine)
    
    if not df_bills.empty:
        col1, col2, col3 = st.columns(3)
        total_rev = df_bills['total_payable'].sum()
        avg_bill = df_bills['total_payable'].mean()
        count = len(df_bills)
        
        col1.metric("Total Revenue", f"₹ {total_rev:,.2f}")
        col2.metric("Bills Generated", count)
        col3.metric("Avg Bill Amount", f"₹ {avg_bill:,.2f}")
        
        # Chart: Bill Distribution
        st.subheader("Bill Amount Distribution")
        fig, ax = plt.subplots()
        df_bills['total_payable'].hist(bins=20, ax=ax, color='skyblue')
        st.pyplot(fig)
    else:
        st.warning("No Bill Data Found. Run the Batch Runner first!")

except Exception as e:
    st.error(f"Database Error: {e}")

st.divider()

# --- Kpi Metric 2: Onboarding/KYC ---
st.header("2. KYC & Onboarding Queue")
try:
    # Assuming you created the 'kyc_records' table from the previous step
    # If not, creates a dummy dataframe for demo
    query_kyc = "SELECT * FROM consumers WHERE kyc_status IS NOT NULL"
    df_kyc = pd.read_sql(query_kyc, engine)
    
    if not df_kyc.empty:
        # Status Breakdown
        status_counts = df_kyc['kyc_status'].value_counts()
        
        col_chart, col_data = st.columns([1, 2])
        
        with col_chart:
            st.write("Application Status")
            st.bar_chart(status_counts)
            
        with col_data:
            st.write("Recent Applications")
            st.dataframe(df_kyc[['name', 'mobile', 'kyc_status']].tail(5))
    else:
        st.info("No KYC Applications yet.")

except Exception as e:
    st.info("KYC Table not found or empty.")

# --- Sidebar Controls ---
st.sidebar.header("Operations")
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

if st.sidebar.button("⚙️ Trigger Batch Job (Manual)"):
    # You can actually import your batch runner and run it here!
    import batch_runner
    with st.spinner('Running Monthly Batch...'):
        batch_runner.run_monthly_batch_job()
    st.success("Batch Complete!")