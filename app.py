# app.py
import streamlit as st
import pandas as pd
import tempfile
import os
from datetime import datetime
from automation import SMSTallyAutomation

# Page configuration
st.set_page_config(
    page_title="SMS & Tally Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #6a5acd;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
    }
    .stat-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 SMS & Tally Reconciliation Tool</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automatically match SMS and Tally data with GST verification</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("Matching Parameters")
    tolerance_days = st.number_input(
        "Tolerance Days", 
        min_value=0, 
        max_value=365, 
        value=30,
        help="Number of days to consider for date matching"
    )
    
    tolerance_amount = st.number_input(
        "Tolerance Amount (₹)", 
        min_value=0.0, 
        value=0.0,
        step=0.1,
        help="Amount difference tolerance for matching"
    )
    
    st.subheader("GST Settings")
    check_gst = st.checkbox(
        "Check GST files for service claims", 
        value=True,
        help="Enable GST verification for service claims"
    )
    
    st.markdown("---")
    st.info("""
    ### 📋 Instructions:
    1. Upload SMS Excel file
    2. Upload Tally Excel file  
    3. Upload GST files (optional)
    4. Click 'Start Processing'
    5. Download results
    """)

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📱 Upload SMS File")
    st.markdown("**Required columns:** TransactionDate, TransactionMode, Description, Remarks, Debit, Credit")
    sms_file = st.file_uploader(
        "Choose SMS Excel file", 
        type=['xlsx', 'xls', 'xlsm'],
        key="sms_uploader"
    )

with col2:
    st.subheader("📋 Upload Tally File")
    st.markdown("**Required columns:** Date, Particulars, Vch Type, Vch No., Debit, Credit")
    tally_file = st.file_uploader(
        "Choose Tally Excel file", 
        type=['xlsx', 'xls', 'xlsm'],
        key="tally_uploader"
    )

st.subheader("🏢 Upload GST Files (Optional)")
st.markdown("**Supported formats:** GST 2A/2B files with invoice values")
gst_files = st.file_uploader(
    "Choose GST Excel files", 
    type=['xlsx', 'xls', 'xlsm'], 
    accept_multiple_files=True,
    key="gst_uploader"
)

# Process button
if st.button("🚀 Start Processing", type="primary", width='stretch'):
    if sms_file and tally_file:
        with st.spinner("Processing files... This may take a few minutes."):
            try:
                # Initialize automation
                automation = SMSTallyAutomation(
                    tolerance_days=tolerance_days,
                    tolerance_amount=tolerance_amount
                )
                
                # Process SMS data
                sms_df = automation.read_excel_file(sms_file)
                sms_df = automation.process_sms_data(sms_df)
                
                # Process Tally data
                tally_df = automation.read_excel_file(tally_file)
                tally_df = automation.process_tally_data(tally_df)
                
                # Match SMS and Tally data
                sms_df, tally_df = automation.match_sms_tally_data(sms_df, tally_df)
                
                # Check GST if enabled
                if check_gst and gst_files:
                    sms_df = automation.check_gst_for_service_claims(sms_df, gst_files)
                    tally_df = automation.check_gst_for_service_claims(tally_df, gst_files)
                
                # Get summary statistics
                stats = automation.get_summary_stats(sms_df, tally_df)
                
                # Display success message
                st.success("✅ Processing completed successfully!")
                
                # Display summary in columns
                st.markdown("### 📈 Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Matched SMS", f"{stats['matched_sms_count']:,}")
                    st.metric("Unmatched SMS", f"{stats['unmatched_sms_count']:,}")
                
                with col2:
                    st.metric("Matched Tally", f"{stats['matched_tally_count']:,}")
                    st.metric("Unmatched Tally", f"{stats['unmatched_tally_count']:,}")
                
                with col3:
                    st.metric("Matched SMS Sum", f"₹{stats['matched_sms_sum']:,.2f}")
                    st.metric("Total SMS Sum", f"₹{stats['total_sms_sum']:,.2f}")
                
                with col4:
                    st.metric("Matched Tally Sum", f"₹{stats['matched_tally_sum']:,.2f}")
                    st.metric("Total Tally Sum", f"₹{stats['total_tally_sum']:,.2f}")
                
                # Check for matching sum discrepancies
                if abs(stats['matched_sms_sum'] - stats['matched_tally_sum']) > 0.01:
                    st.warning("⚠️ Warning: The sum of matched SMS and Tally records does not match!")
                
                # Create tabs for results
                tab1, tab2 = st.tabs(["📱 SMS Results", "📋 Tally Results"])
                
                with tab1:
                    st.subheader("SMS Data Results")
                    
                    # Show matched/unmatched counts
                    matched_count = len(sms_df[sms_df['Status'] == 'Tallied'])
                    unmatched_count = len(sms_df[sms_df['Status'] == 'Not Tallied'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"✅ Matched: {matched_count} records")
                    with col2:
                        st.warning(f"❌ Unmatched: {unmatched_count} records")
                    
                    # Display cleaned SMS data (fix mixed-type issues)
                    sms_display = sms_df.copy()
                    for col in sms_display.columns:
                        if sms_display[col].dtype == 'object':
                            sms_display[col] = sms_display[col].astype(str)

                    st.dataframe(
                        sms_display,
                        width='stretch',
                        height=400
                    )
                    
                    # Download button for SMS results
                    csv = sms_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download SMS Results (CSV)",
                        data=csv,
                        file_name=f"sms_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="secondary"
                    )
                
                with tab2:
                    st.subheader("Tally Data Results")
                    
                    # Show matched/unmatched counts
                    matched_count = len(tally_df[tally_df['Status'] == 'Tallied'])
                    unmatched_count = len(tally_df[tally_df['Status'] == 'Not Tallied'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"✅ Matched: {matched_count} records")
                    with col2:
                        st.warning(f"❌ Unmatched: {unmatched_count} records")
                    
                    # Display cleaned Tally data (fix mixed-type issues)
                    tally_display = tally_df.copy()
                    for col in tally_display.columns:
                        if tally_display[col].dtype == 'object':
                            tally_display[col] = tally_display[col].astype(str)

                    st.dataframe(
                        tally_display,
                        width='stretch',
                        height=400
                    )
                    
                    # Download button for Tally results
                    csv = tally_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Tally Results (CSV)",
                        data=csv,
                        file_name=f"tally_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        type="secondary"
                    )
                
                # Display GST status summary if checked
                if check_gst:
                    st.markdown("### 🏢 GST Verification Summary")
                    
                    # Count GST status for SMS
                    if 'GST Status' in sms_df.columns:
                        sms_gst_counts = sms_df['GST Status'].value_counts()
                        st.write("**SMS GST Status:**")
                        st.write(sms_gst_counts)
                    
                    # Count GST status for Tally
                    if 'GST Status' in tally_df.columns:
                        tally_gst_counts = tally_df['GST Status'].value_counts()
                        st.write("**Tally GST Status:**")
                        st.write(tally_gst_counts)
                
            except Exception as e:
                st.error(f"❌ Error processing files: {str(e)}")
                st.exception(e)
    else:
        st.error("❌ Please upload both SMS and Tally files to proceed.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Step into the future - Embrace learning over manual tasks.</p>
    <p><strong>Proudly initiated by our CEO, Ms. Vandana</strong></p>
    <p>For support: harpinder.singh@rvsolutions.in</p>
</div>
""", unsafe_allow_html=True)