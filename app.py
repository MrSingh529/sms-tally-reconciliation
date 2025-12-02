import streamlit as st
import pandas as pd
import tempfile
import os
import base64
from datetime import datetime
from automation import SMSTallyAutomation

# Page configuration
st.set_page_config(
    page_title="SMS & Tally Reconciliation Pro",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom font function
def load_font(font_path):
    if os.path.exists(font_path):
        try:
            with open(font_path, "rb") as f:
                font_data = f.read()
            return base64.b64encode(font_data).decode()
        except:
            return None
    return None

# Enhanced CSS with modern design
FONT_PATH = "fonts/ClashGrotesk-Regular.ttf"
font_b64 = load_font(FONT_PATH)

if font_b64:
    font_family = f"""
    @font-face {{
        font-family: 'ClashGrotesk';
        src: url(data:font/ttf;base64,{font_b64}) format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    * {{
        font-family: 'ClashGrotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }}
    """
else:
    font_family = ""

custom_css = f"""
<style>
    {font_family}
    
    /* Modern color scheme */
    :root {{
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --bg-light: #f8fafc;
        --text-dark: #1e293b;
        --text-light: #64748b;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Main container styling */
    .block-container {{
        padding: 2rem 3rem;
        max-width: 1400px;
    }}
    
    /* Animated gradient header */
    .hero-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        animation: fadeIn 0.8s ease-in;
    }}
    
    .hero-title {{
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    
    .hero-subtitle {{
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 400;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Modern card design */
    .upload-card {{
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        height: 100%;
    }}
    
    .upload-card:hover {{
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }}
    
    .card-header {{
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .card-description {{
        color: var(--text-light);
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }}
    
    /* Metrics cards */
    .metric-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }}
    
    .metric-card:hover {{
        transform: scale(1.05);
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Status badges */
    .status-badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }}
    
    .status-success {{
        background: #d1fae5;
        color: #065f46;
    }}
    
    .status-warning {{
        background: #fef3c7;
        color: #92400e;
    }}
    
    .status-error {{
        background: #fee2e2;
        color: #991b1b;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }}
    
    /* Enhanced buttons */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
    }}
    
    /* Download button */
    .stDownloadButton > button {{
        background: white;
        color: var(--primary-color);
        border: 2px solid var(--primary-color);
        font-weight: 600;
    }}
    
    .stDownloadButton > button:hover {{
        background: var(--primary-color);
        color: white;
    }}
    
    /* Progress indicator */
    .progress-step {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid var(--primary-color);
    }}
    
    /* Info boxes */
    .info-box {{
        background: linear-gradient(135deg, #e0e7ff 0%, #ddd6fe 100%);
        border-left: 4px solid var(--primary-color);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    .success-box {{
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid var(--success-color);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    .warning-box {{
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid var(--warning-color);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }}
    
    /* File uploader styling */
    .uploadedFile {{
        border: 2px dashed var(--primary-color);
        border-radius: 10px;
        padding: 1rem;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 3rem 0 2rem 0;
        color: var(--text-light);
        border-top: 1px solid #e2e8f0;
        margin-top: 4rem;
    }}
    
    .footer-tagline {{
        font-size: 1.1rem;
        color: var(--text-dark);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🔄 SMS & Tally Reconciliation Pro</div>
    <div class="hero-subtitle">Intelligent data matching with GST verification • Save hours of manual work</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'sms_df' not in st.session_state:
    st.session_state.sms_df = None
if 'tally_df' not in st.session_state:
    st.session_state.tally_df = None

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    with st.expander("📊 Matching Parameters", expanded=True):
        tolerance_days = st.slider(
            "Date Tolerance (days)",
            min_value=0,
            max_value=365,
            value=30,
            help="Maximum days between transactions to consider as a match"
        )
        
        tolerance_amount = st.number_input(
            "Amount Tolerance (₹)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f",
            help="Maximum amount difference to consider as a match"
        )
    
    with st.expander("🔍 GST Verification", expanded=True):
        check_gst = st.checkbox(
            "Enable GST Verification",
            value=True,
            help="Cross-check service claims with GST files"
        )
    
    st.markdown("---")
    
    st.markdown("""
    <div class="info-box">
        <h4 style="margin-top: 0;">📝 Quick Guide</h4>
        <ol style="margin-bottom: 0; padding-left: 1.2rem;">
            <li>Upload your SMS Excel file</li>
            <li>Upload your Tally Excel file</li>
            <li>Add GST files (optional)</li>
            <li>Review settings</li>
            <li>Click Process & Reconcile</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("💡 **Tip:** Hover over any ⓘ icon for detailed help")

# Main content - Step-by-step workflow
st.markdown("## 📤 Step 1: Upload Files")

# File upload section
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="upload-card">
        <div class="card-header">📱 SMS Data File</div>
        <div class="card-description">
            Upload your SMS transaction export<br>
            <strong>Required columns:</strong> TransactionDate, TransactionMode, Description, Remarks, Debit, Credit
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    sms_file = st.file_uploader(
        "Choose SMS Excel file",
        type=['xlsx', 'xls', 'xlsm'],
        key="sms_uploader",
        label_visibility="collapsed"
    )
    
    if sms_file:
        st.success(f"✅ Loaded: {sms_file.name}")
        file_size = len(sms_file.getvalue()) / 1024
        st.caption(f"File size: {file_size:.2f} KB")

with col2:
    st.markdown("""
    <div class="upload-card">
        <div class="card-header">📊 Tally Data File</div>
        <div class="card-description">
            Upload your Tally export file<br>
            <strong>Required columns:</strong> Date, Particulars, Vch Type, Vch No., Debit, Credit
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tally_file = st.file_uploader(
        "Choose Tally Excel file",
        type=['xlsx', 'xls', 'xlsm'],
        key="tally_uploader",
        label_visibility="collapsed"
    )
    
    if tally_file:
        st.success(f"✅ Loaded: {tally_file.name}")
        file_size = len(tally_file.getvalue()) / 1024
        st.caption(f"File size: {file_size:.2f} KB")

# GST files upload
st.markdown("### 📋 GST Files (Optional)")
st.markdown("""
<div class="upload-card" style="padding: 1.5rem;">
    <div class="card-description" style="margin-bottom: 1rem;">
        Upload GST 2A/2B files for verification • Supports multiple files • Helps identify service claims
    </div>
</div>
""", unsafe_allow_html=True)

gst_files = st.file_uploader(
    "Choose GST Excel files",
    type=['xlsx', 'xls', 'xlsm'],
    accept_multiple_files=True,
    key="gst_uploader",
    label_visibility="collapsed"
)

if gst_files:
    st.success(f"✅ Loaded {len(gst_files)} GST file(s)")

st.markdown("---")

# Process button section
st.markdown("## 🚀 Step 2: Process & Reconcile")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button(
        "🔄 Process & Reconcile Data",
        type="primary",
        use_container_width=True,
        disabled=not (sms_file and tally_file)
    )

if not (sms_file and tally_file):
    st.info("👆 Please upload both SMS and Tally files to begin processing")

# Processing logic
if process_button:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Initialize
        status_text.text("🔧 Initializing automation...")
        progress_bar.progress(10)
        automation = SMSTallyAutomation(
            tolerance_days=tolerance_days,
            tolerance_amount=tolerance_amount
        )
        
        # Step 2: Read SMS
        status_text.text("📱 Reading SMS data...")
        progress_bar.progress(25)
        sms_df = automation.read_excel_file(sms_file)
        sms_df = automation.process_sms_data(sms_df)
        
        # Step 3: Read Tally
        status_text.text("📊 Reading Tally data...")
        progress_bar.progress(40)
        tally_df = automation.read_excel_file(tally_file)
        tally_df = automation.process_tally_data(tally_df)
        
        # Step 4: Match data
        status_text.text("🔍 Matching transactions...")
        progress_bar.progress(60)
        sms_df, tally_df = automation.match_sms_tally_data(sms_df, tally_df)
        
        # Step 5: GST verification
        if check_gst and gst_files:
            status_text.text("✓ Verifying GST data...")
            progress_bar.progress(80)
            sms_df = automation.check_gst_for_service_claims(sms_df, gst_files)
            tally_df = automation.check_gst_for_service_claims(tally_df, gst_files)
        
        # Step 6: Complete
        status_text.text("✅ Processing complete!")
        progress_bar.progress(100)
        
        # Store in session state
        st.session_state.processed = True
        st.session_state.sms_df = sms_df
        st.session_state.tally_df = tally_df
        st.session_state.stats = automation.get_summary_stats(sms_df, tally_df)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.success("🎉 Reconciliation completed successfully!")
        st.balloons()
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error during processing: {str(e)}")
        st.exception(e)

# Results section
if st.session_state.processed:
    st.markdown("---")
    st.markdown("## 📈 Step 3: Review Results")
    
    stats = st.session_state.stats
    sms_df = st.session_state.sms_df
    tally_df = st.session_state.tally_df
    
    # Summary metrics
    st.markdown("### Summary Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['matched_sms_count']:,}</div>
            <div class="metric-label">Matched SMS</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats['matched_tally_count']:,}</div>
            <div class="metric-label">Matched Tally</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{stats['matched_sms_sum']/100000:.2f}L</div>
            <div class="metric-label">SMS Amount</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{stats['matched_tally_sum']/100000:.2f}L</div>
            <div class="metric-label">Tally Amount</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Check for discrepancies
    if abs(stats['matched_sms_sum'] - stats['matched_tally_sum']) > 0.01:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Amount Mismatch Detected</strong><br>
            The sum of matched SMS and Tally records differs. Please review the unmatched transactions.
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed results tabs
    tab1, tab2, tab3 = st.tabs(["📱 SMS Results", "📊 Tally Results", "📋 GST Summary"])
    
    with tab1:
        st.markdown("### SMS Transaction Results")
        
        # Status summary
        col1, col2, col3 = st.columns(3)
        matched = len(sms_df[sms_df['Status'] == 'Tallied'])
        unmatched = len(sms_df[sms_df['Status'] == 'Not Tallied'])
        match_rate = (matched / len(sms_df) * 100) if len(sms_df) > 0 else 0
        
        with col1:
            st.metric("Total Records", f"{len(sms_df):,}")
        with col2:
            st.metric("Matched", f"{matched:,}", f"{match_rate:.1f}%")
        with col3:
            st.metric("Unmatched", f"{unmatched:,}")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Tallied", "Not Tallied"],
                key="sms_status_filter"
            )
        with col2:
            search_term = st.text_input(
                "Search in Description",
                key="sms_search",
                placeholder="Enter keywords..."
            )
        
        # Apply filters
        filtered_sms = sms_df.copy()
        if status_filter != "All":
            filtered_sms = filtered_sms[filtered_sms['Status'] == status_filter]
        if search_term:
            filtered_sms = filtered_sms[
                filtered_sms.astype(str).apply(
                    lambda row: row.str.contains(search_term, case=False, na=False).any(),
                    axis=1
                )
            ]
        
        # Display data
        sms_display = filtered_sms.copy()
        for col in sms_display.columns:
            if sms_display[col].dtype == 'object':
                sms_display[col] = sms_display[col].astype(str)
        
        st.dataframe(
            sms_display,
            use_container_width=True,
            height=450,
            hide_index=True
        )
        
        # Download button
        col1, col2 = st.columns([3, 1])
        with col2:
            csv = sms_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"sms_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with tab2:
        st.markdown("### Tally Transaction Results")
        
        # Status summary
        col1, col2, col3 = st.columns(3)
        matched = len(tally_df[tally_df['Status'] == 'Tallied'])
        unmatched = len(tally_df[tally_df['Status'] == 'Not Tallied'])
        match_rate = (matched / len(tally_df) * 100) if len(tally_df) > 0 else 0
        
        with col1:
            st.metric("Total Records", f"{len(tally_df):,}")
        with col2:
            st.metric("Matched", f"{matched:,}", f"{match_rate:.1f}%")
        with col3:
            st.metric("Unmatched", f"{unmatched:,}")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Tallied", "Not Tallied"],
                key="tally_status_filter"
            )
        with col2:
            search_term = st.text_input(
                "Search in Particulars",
                key="tally_search",
                placeholder="Enter keywords..."
            )
        
        # Apply filters
        filtered_tally = tally_df.copy()
        if status_filter != "All":
            filtered_tally = filtered_tally[filtered_tally['Status'] == status_filter]
        if search_term:
            filtered_tally = filtered_tally[
                filtered_tally.astype(str).apply(
                    lambda row: row.str.contains(search_term, case=False, na=False).any(),
                    axis=1
                )
            ]
        
        # Display data
        tally_display = filtered_tally.copy()
        for col in tally_display.columns:
            if tally_display[col].dtype == 'object':
                tally_display[col] = tally_display[col].astype(str)
        
        st.dataframe(
            tally_display,
            use_container_width=True,
            height=450,
            hide_index=True
        )
        
        # Download button
        col1, col2 = st.columns([3, 1])
        with col2:
            csv = tally_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"tally_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with tab3:
        st.markdown("### GST Verification Summary")
        
        if check_gst and 'GST Status' in sms_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### SMS GST Status")
                sms_gst_counts = sms_df['GST Status'].value_counts()
                for status, count in sms_gst_counts.items():
                    percentage = (count / len(sms_df) * 100)
                    st.metric(status, f"{count:,}", f"{percentage:.1f}%")
            
            with col2:
                st.markdown("#### Tally GST Status")
                tally_gst_counts = tally_df['GST Status'].value_counts()
                for status, count in tally_gst_counts.items():
                    percentage = (count / len(tally_df) * 100)
                    st.metric(status, f"{count:,}", f"{percentage:.1f}%")
        else:
            st.info("GST verification was not enabled or no GST files were uploaded.")

# Footer
st.markdown("""
<div class="footer">
    <div class="footer-tagline">Step into the future - Embrace learning over manual tasks</div>
    <p><strong>Embrace Automation</strong> by Harpinder Singh</p>
    <p>For Support: <a href="mailto:harpinder.singh@rvsolutions.in">harpinder.singh@rvsolutions.in</a></p>
</div>
""", unsafe_allow_html=True)