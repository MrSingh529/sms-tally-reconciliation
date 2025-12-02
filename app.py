import streamlit as st
import pandas as pd
import tempfile
import os
import base64
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from automation import SMSTallyAutomation

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="SMS & Tally Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.rvsolutions.in',
        'Report a bug': "mailto:harpinder.singh@rvsolutions.in",
        'About': "### SMS & Tally Reconciliation Tool\nAutomatically match SMS and Tally data with GST verification"
    }
)

# ========== CUSTOM CSS & STYLING ==========
def load_custom_css():
    """Load and inject custom CSS for professional styling"""
    css = """
    <style>
        /* Main theme colors */
        :root {
            --primary: #6a5acd;
            --primary-dark: #5a4bbc;
            --secondary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --light: #f8fafc;
            --dark: #1e293b;
            --gray: #94a3b8;
        }
        
        /* Global styles */
        .main {
            padding: 0 1rem;
        }
        
        /* Custom headers */
        .main-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
        }
        
        .sub-header {
            color: var(--gray);
            font-size: 1.1rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        /* Card styling */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-left: 4px solid var(--primary);
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        
        .upload-card {
            background: white;
            border: 2px dashed #e2e8f0;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .upload-card:hover {
            border-color: var(--primary);
            background-color: #f8fafc;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 2rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:focus {
            box-shadow: 0 0 0 3px rgba(106, 90, 205, 0.3);
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        }
        
        /* Data table styling */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        .dataframe th {
            background-color: var(--primary) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .status-matched {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .status-unmatched {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        .status-pending {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--gray);
            font-size: 0.9rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 3rem;
        }
        
        /* Animation for success */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .success-pulse {
            animation: pulse 2s infinite;
        }
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load custom CSS
load_custom_css()

# ========== SESSION STATE INITIALIZATION ==========
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'results_data' not in st.session_state:
    st.session_state.results_data = None
if 'summary_stats' not in st.session_state:
    st.session_state.summary_stats = None

# ========== HELPER FUNCTIONS ==========
def create_progress_bar(step, total_steps):
    """Create a progress bar for processing steps"""
    progress = step / total_steps
    progress_bar = st.progress(0)
    
    for i in range(int(progress * 100)):
        progress_bar.progress(i + 1)
    
    return progress_bar

def create_metric_card(title, value, change=None, icon=None):
    """Create a metric card with optional change indicator"""
    icon_html = f"<span style='font-size: 1.5rem; margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    change_html = ""
    
    if change is not None:
        color = "green" if change >= 0 else "red"
        arrow = "↑" if change >= 0 else "↓"
        change_html = f"<span style='color: {color}; font-size: 0.9rem;'> {arrow} {abs(change):.1f}%</span>"
    
    card_html = f"""
    <div class='metric-card'>
        <div style='color: var(--gray); font-size: 0.9rem; margin-bottom: 0.5rem;'>{title}</div>
        <div style='font-size: 1.8rem; font-weight: 700; color: var(--dark);'>
            {icon_html}{value}{change_html}
        </div>
    </div>
    """
    return card_html

def create_summary_charts(stats):
    """Create summary charts using Plotly"""
    fig1 = go.Figure(data=[
        go.Pie(
            labels=['Matched', 'Unmatched'],
            values=[stats['matched_sms_count'], stats['unmatched_sms_count']],
            hole=.4,
            marker_colors=['#10b981', '#ef4444']
        )
    ])
    fig1.update_layout(
        title="SMS Records Distribution",
        showlegend=True,
        height=300
    )
    
    fig2 = go.Figure(data=[
        go.Pie(
            labels=['Matched', 'Unmatched'],
            values=[stats['matched_tally_count'], stats['unmatched_tally_count']],
            hole=.4,
            marker_colors=['#10b981', '#ef4444']
        )
    ])
    fig2.update_layout(
        title="Tally Records Distribution",
        showlegend=True,
        height=300
    )
    
    return fig1, fig2

# ========== HEADER SECTION ==========
st.markdown('<h1 class="main-header">📊 SMS & Tally Reconciliation</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automate financial reconciliation with intelligent matching and GST verification</p>', unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/data-configuration.png", width=80)
    st.markdown("### ⚙️ Configuration")
    
    with st.expander("Matching Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            tolerance_days = st.number_input(
                "Date Tolerance (Days)", 
                min_value=0, 
                max_value=365, 
                value=30,
                help="Maximum days difference for matching"
            )
        with col2:
            tolerance_amount = st.number_input(
                "Amount Tolerance (₹)", 
                min_value=0.0, 
                value=0.0,
                step=0.1,
                format="%.2f",
                help="Maximum amount difference for matching"
            )
    
    with st.expander("Advanced Settings", expanded=False):
        check_gst = st.checkbox(
            "Enable GST Verification", 
            value=True,
            help="Verify service claims against GST files"
        )
        enable_notifications = st.checkbox(
            "Email Notifications", 
            value=False,
            help="Send results via email"
        )
        auto_download = st.checkbox(
            "Auto-download Results", 
            value=False,
            help="Automatically download results after processing"
        )
    
    st.markdown("---")
    
    with st.expander("📚 How to Use", expanded=False):
        st.markdown("""
        1. **Upload Files**
           - SMS file (Excel format)
           - Tally file (Excel format)
           - GST files (Optional, for verification)
        
        2. **Configure Settings**
           - Set matching tolerances
           - Enable GST verification
        
        3. **Process & Review**
           - Start processing
           - Review matches
           - Download results
        
        4. **Export Results**
           - Download as CSV
           - Generate reports
        """)
    
    st.markdown("---")
    st.info("💡 **Tip**: Upload GST files for comprehensive service claim verification.")
    st.caption(f"v1.0 • {datetime.now().strftime('%Y-%m-%d')}")

# ========== MAIN CONTENT ==========
# File Upload Section
st.markdown("## 📁 File Upload")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown("### 📱 SMS Data")
        st.markdown("**Required columns:**")
        st.caption("TransactionDate, TransactionMode, Description, Remarks, Debit, Credit")
        sms_file = st.file_uploader(
            "Upload SMS Excel",
            type=['xlsx', 'xls', 'xlsm'],
            key="sms_uploader",
            label_visibility="collapsed"
        )
        if sms_file:
            st.success(f"✓ {sms_file.name}")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown("### 🏢 Tally Data")
        st.markdown("**Required columns:**")
        st.caption("Date, Particulars, Vch Type, Vch No., Debit, Credit")
        tally_file = st.file_uploader(
            "Upload Tally Excel",
            type=['xlsx', 'xls', 'xlsm'],
            key="tally_uploader",
            label_visibility="collapsed"
        )
        if tally_file:
            st.success(f"✓ {tally_file.name}")
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown("### 📄 GST Files")
        st.markdown("**Optional verification**")
        st.caption("GST 2A/2B files for service claims")
        gst_files = st.file_uploader(
            "Upload GST Files",
            type=['xlsx', 'xls', 'xlsm'],
            accept_multiple_files=True,
            key="gst_uploader",
            label_visibility="collapsed"
        )
        if gst_files:
            st.success(f"✓ {len(gst_files)} files uploaded")
        st.markdown('</div>', unsafe_allow_html=True)

# Process Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_btn = st.button(
        "🚀 Start Reconciliation",
        type="primary",
        use_container_width=True,
        disabled=not (sms_file and tally_file)
    )

# Processing Logic
if process_btn and sms_file and tally_file:
    with st.spinner("🔄 Initializing reconciliation process..."):
        try:
            # Initialize progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Initialize automation
            status_text.text("Step 1/5: Initializing automation engine...")
            automation = SMSTallyAutomation(
                tolerance_days=tolerance_days,
                tolerance_amount=tolerance_amount
            )
            progress_bar.progress(20)
            
            # Step 2: Process SMS data
            status_text.text("Step 2/5: Processing SMS data...")
            sms_df = automation.read_excel_file(sms_file)
            sms_df = automation.process_sms_data(sms_df)
            progress_bar.progress(40)
            
            # Step 3: Process Tally data
            status_text.text("Step 3/5: Processing Tally data...")
            tally_df = automation.read_excel_file(tally_file)
            tally_df = automation.process_tally_data(tally_df)
            progress_bar.progress(60)
            
            # Step 4: Match data
            status_text.text("Step 4/5: Matching SMS and Tally records...")
            sms_df, tally_df = automation.match_sms_tally_data(sms_df, tally_df)
            progress_bar.progress(80)
            
            # Step 5: GST verification
            if check_gst and gst_files:
                status_text.text("Step 5/5: Verifying GST records...")
                sms_df = automation.check_gst_for_service_claims(sms_df, gst_files)
                tally_df = automation.check_gst_for_service_claims(tally_df, gst_files)
            progress_bar.progress(100)
            
            # Get summary statistics
            stats = automation.get_summary_stats(sms_df, tally_df)
            
            # Store results in session state
            st.session_state.processing_complete = True
            st.session_state.results_data = {
                'sms_df': sms_df,
                'tally_df': tally_df
            }
            st.session_state.summary_stats = stats
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Show success animation
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            st.exception(e)

# Display Results if Processing Complete
if st.session_state.processing_complete:
    stats = st.session_state.summary_stats
    sms_df = st.session_state.results_data['sms_df']
    tally_df = st.session_state.results_data['tally_df']
    
    # Success Message
    success_col1, success_col2, success_col3 = st.columns([1, 2, 1])
    with success_col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                    border-radius: 12px; margin: 2rem 0;' class='success-pulse'>
            <h2 style='color: #065f46;'>✅ Processing Complete!</h2>
            <p style='color: #047857;'>Reconciliation successfully completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary Metrics
    st.markdown("## 📈 Summary Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total SMS Records", 
            f"{stats['total_sms_count']:,}",
            icon="📱"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Total Tally Records", 
            f"{stats['total_tally_count']:,}",
            icon="🏢"
        ), unsafe_allow_html=True)
    
    with col3:
        match_rate = (stats['matched_sms_count'] / stats['total_sms_count'] * 100) if stats['total_sms_count'] > 0 else 0
        st.markdown(create_metric_card(
            "Match Rate", 
            f"{match_rate:.1f}%",
            icon="✅"
        ), unsafe_allow_html=True)
    
    with col4:
        total_amount = stats['total_sms_sum'] + stats['total_tally_sum']
        st.markdown(create_metric_card(
            "Total Amount", 
            f"₹{total_amount:,.2f}",
            icon="💰"
        ), unsafe_allow_html=True)
    
    # Charts
    st.markdown("## 📊 Visualization")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig1, fig2 = create_summary_charts(stats)
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(fig2, use_container_width=True)
    
    # Results Tabs
    st.markdown("## 📋 Detailed Results")
    tab1, tab2, tab3 = st.tabs(["📱 SMS Results", "🏢 Tally Results", "⚖️ Comparison"])
    
    with tab1:
        st.subheader("SMS Reconciliation Results")
        
        # SMS Metrics
        sms_col1, sms_col2, sms_col3 = st.columns(3)
        with sms_col1:
            st.metric("Matched Records", f"{stats['matched_sms_count']:,}", 
                     f"{stats['matched_sms_count']/stats['total_sms_count']*100:.1f}%")
        with sms_col2:
            st.metric("Matched Amount", f"₹{stats['matched_sms_sum']:,.2f}",
                     f"{stats['matched_sms_sum']/stats['total_sms_sum']*100:.1f}%" if stats['total_sms_sum'] > 0 else "0%")
        with sms_col3:
            st.metric("Unmatched Amount", f"₹{stats['total_sms_sum'] - stats['matched_sms_sum']:,.2f}")
        
        # SMS Dataframe with styling
        st.dataframe(
            sms_df,
            use_container_width=True,
            height=400,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Tallied or Not Tallied"
                ),
                "GST Status": st.column_config.TextColumn(
                    "GST Status",
                    help="GST verification status"
                )
            }
        )
        
        # Download buttons for SMS
        col1, col2 = st.columns(2)
        with col1:
            csv = sms_df.to_csv(index=False)
            st.download_button(
                label="📥 Download SMS Results (CSV)",
                data=csv,
                file_name=f"sms_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="secondary",
                use_container_width=True
            )
        with col2:
            # Excel download option
            excel_buffer = pd.ExcelWriter(tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name)
            sms_df.to_excel(excel_buffer, index=False)
            excel_buffer.save()
            
            with open(excel_buffer.name, 'rb') as f:
                excel_data = f.read()
            
            st.download_button(
                label="📊 Download SMS Results (Excel)",
                data=excel_data,
                file_name=f"sms_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab2:
        st.subheader("Tally Reconciliation Results")
        
        # Tally Metrics
        tally_col1, tally_col2, tally_col3 = st.columns(3)
        with tally_col1:
            st.metric("Matched Records", f"{stats['matched_tally_count']:,}",
                     f"{stats['matched_tally_count']/stats['total_tally_count']*100:.1f}%")
        with tally_col2:
            st.metric("Matched Amount", f"₹{stats['matched_tally_sum']:,.2f}",
                     f"{stats['matched_tally_sum']/stats['total_tally_sum']*100:.1f}%" if stats['total_tally_sum'] > 0 else "0%")
        with tally_col3:
            st.metric("Unmatched Amount", f"₹{stats['total_tally_sum'] - stats['matched_tally_sum']:,.2f}")
        
        # Tally Dataframe
        st.dataframe(
            tally_df,
            use_container_width=True,
            height=400
        )
        
        # Download buttons for Tally
        col1, col2 = st.columns(2)
        with col1:
            csv = tally_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Tally Results (CSV)",
                data=csv,
                file_name=f"tally_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="secondary",
                use_container_width=True
            )
        with col2:
            # Excel download option
            excel_buffer = pd.ExcelWriter(tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx').name)
            tally_df.to_excel(excel_buffer, index=False)
            excel_buffer.save()
            
            with open(excel_buffer.name, 'rb') as f:
                excel_data = f.read()
            
            st.download_button(
                label="📊 Download Tally Results (Excel)",
                data=excel_data,
                file_name=f"tally_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with tab3:
        st.subheader("Reconciliation Summary")
        
        # Comparison metrics
        st.markdown("### Match Comparison")
        
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        with comp_col1:
            st.info(f"**Total Matched Records:** {stats['matched_sms_count'] + stats['matched_tally_count']:,}")
        with comp_col2:
            st.info(f"**Total Unmatched Records:** {stats['unmatched_sms_count'] + stats['unmatched_tally_count']:,}")
        with comp_col3:
            discrepancy = abs(stats['matched_sms_sum'] - stats['matched_tally_sum'])
            if discrepancy > 0.01:
                st.warning(f"**Amount Discrepancy:** ₹{discrepancy:,.2f}")
            else:
                st.success("**Amount Discrepancy:** ₹0.00 ✓")
        
        # Detailed match analysis
        st.markdown("### Detailed Analysis")
        
        analysis_df = pd.DataFrame({
            'Metric': ['Total Records', 'Matched Records', 'Unmatched Records', 'Total Amount', 'Matched Amount'],
            'SMS': [
                stats['total_sms_count'],
                stats['matched_sms_count'],
                stats['unmatched_sms_count'],
                stats['total_sms_sum'],
                stats['matched_sms_sum']
            ],
            'Tally': [
                stats['total_tally_count'],
                stats['matched_tally_count'],
                stats['unmatched_tally_count'],
                stats['total_tally_sum'],
                stats['matched_tally_sum']
            ]
        })
        
        st.dataframe(analysis_df, use_container_width=True)
        
        # Export full report
        st.markdown("### 📑 Export Full Report")
        
        if st.button("Generate Comprehensive Report", type="primary", use_container_width=True):
            with st.spinner("Generating report..."):
                # Create a comprehensive report
                report_data = {
                    'summary_stats': stats,
                    'sms_data': sms_df.head(1000).to_dict('records'),  # Limit for performance
                    'tally_data': tally_df.head(1000).to_dict('records')
                }
                
                # For demo, create a simple text report
                report_text = f"""
                SMS & Tally Reconciliation Report
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                SUMMARY:
                ========
                Total SMS Records: {stats['total_sms_count']:,}
                Total Tally Records: {stats['total_tally_count']:,}
                Match Rate: {(stats['matched_sms_count']/stats['total_sms_count']*100):.1f}%
                
                AMOUNTS:
                ========
                Total SMS Amount: ₹{stats['total_sms_sum']:,.2f}
                Total Tally Amount: ₹{stats['total_tally_sum']:,.2f}
                Matched SMS Amount: ₹{stats['matched_sms_sum']:,.2f}
                Matched Tally Amount: ₹{stats['matched_tally_sum']:,.2f}
                
                DISCREPANCIES:
                =============
                Unmatched SMS Records: {stats['unmatched_sms_count']:,}
                Unmatched Tally Records: {stats['unmatched_tally_count']:,}
                Amount Discrepancy: ₹{abs(stats['matched_sms_sum'] - stats['matched_tally_sum']):,.2f}
                """
                
                st.download_button(
                    label="Download Full Report (TXT)",
                    data=report_text,
                    file_name=f"reconciliation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# Empty State - Before Processing
elif not st.session_state.processing_complete:
    st.markdown("""
    <div style='text-align: center; padding: 4rem; color: var(--gray);'>
        <h3>👋 Welcome to Reconciliation Tool</h3>
        <p>Upload your SMS and Tally files to begin the reconciliation process.</p>
        <p style='font-size: 0.9rem; margin-top: 2rem;'>
            <strong>Need help?</strong> Check the sidebar for instructions.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p style='margin-bottom: 0.5rem;'>
        <strong>Step into the future - Embrace learning over manual tasks.</strong>
    </p>
    <p style='margin-bottom: 0.5rem; color: var(--primary);'>
        🚀 Embrace Automation | Harpinder Singh
    </p>
    <p style='font-size: 0.8rem;'>
        For Support: harpinder.singh@rvsolutions.in | 
        Version 1.0 • © 2024 RV Solutions
    </p>
</div>
""", unsafe_allow_html=True)