import streamlit as st
import pandas as pd
import tempfile
import os
import base64
from datetime import datetime
from automation import SMSTallyAutomation
from chatbot import Chatbot

def create_template_files():
    """Create template files if they don't exist"""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)

    template_files = [
        ("Tally_Template.xlsx", "Tally Transaction Template"),
        ("SMS_Template.xlsx", "SMS Transaction Template"),
        ("GST_Format1.xlsx", "GST Template Format 1"),
        ("GST_Format2.xlsx", "GST Template Format 2")
    ]

    for filename, description in template_files:
        filepath = os.path.join(templates_dir, filename)
        if not os.path.exists(filepath):
            import pandas as pd
            if "Tally" in filename:
                df = pd.DataFrame(columns=['Date', 'Particulars', 'Vch Type', 'Vch No.', 'Debit', 'Credit', 'Notes'])
            elif "SMS" in filename:
                df = pd.DataFrame(columns=['TransactionDate', 'TransactionMode', 'Description', 'Remarks', 'Debit', 'Credit', 'PaymentMode'])
            elif "GST" in filename:
                df = pd.DataFrame(columns=['Invoice No', 'Invoice Date', 'Invoice Value', 'GSTIN', 'Supplier Name'])

            df.to_excel(filepath, index=False)

    return templates_dir
# --------------------------------------------------------


# Page configuration
st.set_page_config(
    page_title="Reconciliation Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<!-- Load Material Icons -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Restore Material Icons Font (fix icon showing as text) */
    .material-icons,
    .material-icons-outlined,
    .material-icons-round,
    .material-icons-sharp,
    .material-icons-two-tone,
    [class^="material-icons"] {
        font-family: 'Material Icons' !important;
        speak: none;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        letter-spacing: normal;
        -webkit-font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
    }

    /* Global styling (apply Inter broadly) */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* Force Inter for headings / titles */
    .app-title,
    .app-subtitle,
    .card-header,
    .metric-label,
    .metric-value,
    .upload-text,
    .upload-subtext,
    .footer-tagline,
    .footer-credits {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Fix sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
    }

    [data-testid="collapsedControl"] svg {
        display: block !important;
    }

    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0 !important;
    }

    /* Custom header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 3rem;
        margin: -6rem -6rem 2rem -6rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .app-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        opacity: 0.95;
    }

    /* Card styling */
    .custom-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e8ecef;
        transition: all 0.3s ease;
    }

    .custom-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }

    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #f7fafc;
    }

    /* Metric cards */
    .metric-card {
        background: transparent;
        border-radius: 0;
        padding: 1.5rem 0;
        color: #1a202c;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: #1a202c;
    }

    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #718096;
    }

    .metric-card.success .metric-value { color: #059669; }
    .metric-card.warning .metric-value { color: #dc2626; }
    .metric-card.info .metric-value { color: #2563eb; }

    /* Upload zone */
    .upload-zone {
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f7fafc;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .upload-zone:hover {
        border-color: #667eea;
        background: #edf2f7;
    }

    .upload-icon {
        font-size: 3rem;
        color: #a0aec0;
        margin-bottom: 1rem;
    }

    .upload-text {
        color: #4a5568;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .upload-subtext {
        color: #718096;
        font-size: 0.875rem;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e8ecef;
    }

    /* Inputs */
    .stNumberInput input,
    .stSelectbox div,
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem 0.75rem;
        transition: all 0.2s ease;
    }

    .stNumberInput input:focus,
    .stSelectbox div:focus,
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Alerts */
    .success-alert {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: #22543d;
        font-weight: 500;
        border-left: 4px solid #38a169;
        margin: 1rem 0;
    }

    .warning-alert {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: #7c2d12;
        font-weight: 500;
        border-left: 4px solid #dd6b20;
        margin: 1rem 0;
    }

    .info-alert {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: #1e40af;
        font-weight: 500;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        background: white;
        border-radius: 12px;
        margin-top: 3rem;
        border: 1px solid #e8ecef;
    }

    .footer-tagline {
        font-size: 1rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 0.5rem;
    }

    .footer-credits {
        font-size: 0.875rem;
        color: #718096;
    }
            
    .chat-container {
        position: fixed;
        bottom: 100px;
        right: 20px;
        width: 400px;
        height: 500px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #e8ecef;
    }
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-messages {
        flex: 1;
        padding: 15px;
        overflow-y: auto;
        background: #f8f9fa;
    }
    .chat-message {
        margin-bottom: 15px;
        max-width: 80%;
    }
    .chat-message.bot { margin-right: auto; }
    .chat-message.user { margin-left: auto; }
    .message-bubble {
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
    }
    .bot .message-bubble {
        background: white;
        border: 1px solid #e8ecef;
        color: #333;
    }
    .user .message-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .chat-options {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 10px;
    }
    .chat-option-button {
        background: white;
        border: 1px solid #e8ecef;
        border-radius: 8px;
        padding: 10px 15px;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 14px;
    }
    .chat-option-button:hover {
        background: #f8f9fa;
        border-color: #667eea;
        transform: translateY(-1px);
    }
    .close-chat {
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }
    .close-chat:hover {
        background: rgba(255,255,255,0.2);
    }
    .stButton > button[kind="secondary"] {
        background: white;
        color: #4a5568;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        margin: 2px 0;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f7fafc;
        border-color: #cbd5e0;
        transform: translateY(-1px);
    }
    
    /* Floating button styling */
    .floating-chat-btn .stButton > button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-size: 24px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .floating-chat-btn .stButton > button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

chatbot = Chatbot()
create_template_files()

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">Reconciliation Suite</h1>
    <p class="app-subtitle">SMS and Tally reconciliation with automated GST verification</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown('<div class="card-header">Configuration</div>', unsafe_allow_html=True)
    
    st.markdown("#### Matching Parameters")
    tolerance_days = st.number_input(
        "Date Tolerance (days)", 
        min_value=0, 
        max_value=365, 
        value=30,
        help="Number of days to consider for date matching"
    )
    
    tolerance_amount = st.number_input(
        "Amount Tolerance (₹)", 
        min_value=0.0, 
        value=0.0,
        step=0.1,
        help="Amount difference tolerance for matching"
    )
    
    st.markdown("#### GST Verification")
    check_gst = st.checkbox(
        "Enable GST verification", 
        value=True,
        help="Check GST files for service claims validation"
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div class="info-alert">
        <strong>Quick Guide</strong><br>
        1. Upload SMS data file<br>
        2. Upload Tally data file<br>
        3. Add GST files (optional)<br>
        4. Configure parameters<br>
        5. Process and download results
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="custom-card">
        <div class="card-header">SMS Data Upload</div>
        <p style="color: #718096; margin-bottom: 1rem;">Upload your SMS transaction data file</p>
    </div>
    """, unsafe_allow_html=True)
    
    sms_file = st.file_uploader(
        "Choose SMS Excel file", 
        type=['xlsx', 'xls', 'xlsm'],
        key="sms_uploader",
        label_visibility="collapsed"
    )
    
    if sms_file:
        st.markdown("""
        <div class="success-alert">
            File uploaded successfully: <strong>{}</strong>
        </div>
        """.format(sms_file.name), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="custom-card">
        <div class="card-header">Tally Data Upload</div>
        <p style="color: #718096; margin-bottom: 1rem;">Upload your Tally transaction data file</p>
    </div>
    """, unsafe_allow_html=True)
    
    tally_file = st.file_uploader(
        "Choose Tally Excel file", 
        type=['xlsx', 'xls', 'xlsm'],
        key="tally_uploader",
        label_visibility="collapsed"
    )
    
    if tally_file:
        st.markdown("""
        <div class="success-alert">
            File uploaded successfully: <strong>{}</strong>
        </div>
        """.format(tally_file.name), unsafe_allow_html=True)

# GST files section
st.markdown("""
<div class="custom-card">
    <div class="card-header">GST Files (Optional)</div>
    <p style="color: #718096; margin-bottom: 1rem;">Upload GST 2A/2B files for verification</p>
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
    st.markdown("""
    <div class="info-alert">
        {} GST file(s) uploaded successfully
    </div>
    """.format(len(gst_files)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button("Start Reconciliation Process", type="primary", use_container_width=True)

if process_button:
    if sms_file and tally_file:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize automation
            status_text.markdown('<div class="info-alert">Initializing reconciliation engine...</div>', unsafe_allow_html=True)
            progress_bar.progress(10)
            automation = SMSTallyAutomation(
                tolerance_days=tolerance_days,
                tolerance_amount=tolerance_amount
            )
            
            # Process SMS data
            status_text.markdown('<div class="info-alert">Processing SMS data...</div>', unsafe_allow_html=True)
            progress_bar.progress(25)
            sms_df = automation.read_excel_file(sms_file)
            sms_df = automation.process_sms_data(sms_df)
            
            # Process Tally data
            status_text.markdown('<div class="info-alert">Processing Tally data...</div>', unsafe_allow_html=True)
            progress_bar.progress(45)
            tally_df = automation.read_excel_file(tally_file)
            tally_df = automation.process_tally_data(tally_df)
            
            # Match data
            status_text.markdown('<div class="info-alert">Matching transactions...</div>', unsafe_allow_html=True)
            progress_bar.progress(65)
            sms_df, tally_df = automation.match_sms_tally_data(sms_df, tally_df)
            
            # Check GST if enabled
            if check_gst and gst_files:
                status_text.markdown('<div class="info-alert">Verifying GST claims...</div>', unsafe_allow_html=True)
                progress_bar.progress(85)
                sms_df = automation.check_gst_for_service_claims(sms_df, gst_files)
                tally_df = automation.check_gst_for_service_claims(tally_df, gst_files)
            
            # Get summary statistics
            progress_bar.progress(95)
            stats = automation.get_summary_stats(sms_df, tally_df)
            
            progress_bar.progress(100)
            status_text.markdown('<div class="success-alert">Reconciliation completed successfully</div>', unsafe_allow_html=True)
            
            st.session_state.processing_complete = True
            st.session_state.results = {
                'sms_df': sms_df,
                'tally_df': tally_df,
                'stats': stats
            }
            
            # Display results
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="card-header">Reconciliation Results</div>', unsafe_allow_html=True)
            
            # Metrics in cards
            col1, col2, col3, col4 = st.columns(4, gap="medium")
            
            with col1:
                st.markdown("""
                <div class="metric-card success">
                    <div class="metric-label">Matched SMS</div>
                    <div class="metric-value">{:,}</div>
                </div>
                """.format(stats['matched_sms_count']), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="metric-card warning">
                    <div class="metric-label">Unmatched SMS</div>
                    <div class="metric-value">{:,}</div>
                </div>
                """.format(stats['unmatched_sms_count']), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card success">
                    <div class="metric-label">Matched Tally</div>
                    <div class="metric-value">{:,}</div>
                </div>
                """.format(stats['matched_tally_count']), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="metric-card warning">
                    <div class="metric-label">Unmatched Tally</div>
                    <div class="metric-value">{:,}</div>
                </div>
                """.format(stats['unmatched_tally_count']), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card info">
                    <div class="metric-label">Matched SMS Sum</div>
                    <div class="metric-value">₹{:,.0f}</div>
                </div>
                """.format(stats['matched_sms_sum']), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Total SMS Sum</div>
                    <div class="metric-value">₹{:,.0f}</div>
                </div>
                """.format(stats['total_sms_sum']), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="metric-card info">
                    <div class="metric-label">Matched Tally Sum</div>
                    <div class="metric-value">₹{:,.0f}</div>
                </div>
                """.format(stats['matched_tally_sum']), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Total Tally Sum</div>
                    <div class="metric-value">₹{:,.0f}</div>
                </div>
                """.format(stats['total_tally_sum']), unsafe_allow_html=True)
            
            # Check for discrepancies
            if abs(stats['matched_sms_sum'] - stats['matched_tally_sum']) > 0.01:
                st.markdown("""
                <div class="warning-alert">
                    <strong>Attention:</strong> Sum mismatch detected between matched SMS and Tally records. Please review the data.
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Results tabs
            tab1, tab2 = st.tabs(["SMS Results", "Tally Results"])
            
            with tab1:
                st.markdown('<div class="card-header">SMS Transaction Results</div>', unsafe_allow_html=True)
                
                matched_count = len(sms_df[sms_df['Status'] == 'Tallied'])
                unmatched_count = len(sms_df[sms_df['Status'] == 'Not Tallied'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="success-alert">
                        <strong>Matched Records:</strong> {:,}
                    </div>
                    """.format(matched_count), unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="warning-alert">
                        <strong>Unmatched Records:</strong> {:,}
                    </div>
                    """.format(unmatched_count), unsafe_allow_html=True)
                
                # Display data
                sms_display = sms_df.copy()
                for col in sms_display.columns:
                    if sms_display[col].dtype == 'object':
                        sms_display[col] = sms_display[col].astype(str)
                
                st.dataframe(sms_display, use_container_width=True, height=400)
                
                # Download button
                csv = sms_df.to_csv(index=False)
                st.download_button(
                    label="Download SMS Results",
                    data=csv,
                    file_name=f"sms_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with tab2:
                st.markdown('<div class="card-header">Tally Transaction Results</div>', unsafe_allow_html=True)
                
                matched_count = len(tally_df[tally_df['Status'] == 'Tallied'])
                unmatched_count = len(tally_df[tally_df['Status'] == 'Not Tallied'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div class="success-alert">
                        <strong>Matched Records:</strong> {:,}
                    </div>
                    """.format(matched_count), unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="warning-alert">
                        <strong>Unmatched Records:</strong> {:,}
                    </div>
                    """.format(unmatched_count), unsafe_allow_html=True)
                
                # Display data
                tally_display = tally_df.copy()
                for col in tally_display.columns:
                    if tally_display[col].dtype == 'object':
                        tally_display[col] = tally_display[col].astype(str)
                
                st.dataframe(tally_display, use_container_width=True, height=400)
                
                # Download button
                csv = tally_df.to_csv(index=False)
                st.download_button(
                    label="Download Tally Results",
                    data=csv,
                    file_name=f"tally_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # GST summary if applicable
            if check_gst:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="card-header">GST Verification Summary</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'GST Status' in sms_df.columns:
                        st.markdown("**SMS GST Status Distribution**")
                        sms_gst_counts = sms_df['GST Status'].value_counts()
                        st.dataframe(sms_gst_counts, use_container_width=True)
                
                with col2:
                    if 'GST Status' in tally_df.columns:
                        st.markdown("**Tally GST Status Distribution**")
                        tally_gst_counts = tally_df['GST Status'].value_counts()
                        st.dataframe(tally_gst_counts, use_container_width=True)
            
        except Exception as e:
            progress_bar.empty()
            status_text.markdown("""
            <div class="warning-alert">
                <strong>Error:</strong> {}
            </div>
            """.format(str(e)), unsafe_allow_html=True)
            st.exception(e)
    else:
        st.markdown("""
        <div class="warning-alert">
            <strong>Missing Files:</strong> Please upload both SMS and Tally files to begin reconciliation.
        </div>
        """, unsafe_allow_html=True)

chatbot.render_chat_button()

# Handle chat window
if st.session_state.get("chat_open", False):
    # Create a container with fixed positioning
    st.markdown("""
    <style>
    .chat-window-container {
        position: fixed;
        bottom: 100px;
        right: 20px;
        width: 400px;
        height: 500px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 9999;
        border: 1px solid #e8ecef;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main chat container
    with st.container():
        st.markdown('<div class="chat-window-container">', unsafe_allow_html=True)
        
        # Close button at top-right
        col1, col2, col3 = st.columns([5, 1, 1])
        with col3:
            if st.button("×", key="close_chat_btn"):
                st.session_state.chat_open = False
                st.rerun()
        
        # Render chat interface
        chatbot.render_chat_interface()
        
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------- CHATBOT DOWNLOAD HANDLER -----------------------
if "trigger_download" in st.session_state:
    file_info = st.session_state["trigger_download"]

    if os.path.exists(file_info.get("local_path", "")):
        with open(file_info["local_path"], "rb") as file:
            data = file.read()

        st.download_button(
            label=f"Click to download {file_info['filename']}",
            data=data,
            file_name=file_info["filename"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="auto_download"
        )

    del st.session_state["trigger_download"]

# Footer
st.markdown("""
<div class="app-footer">
    <p class="footer-tagline">Step into the future - Embrace learning over manual tasks</p>
    <p class="footer-credits"><strong>Embrace Automation</strong> - Harpinder Singh</p>
    <p class="footer-credits">For Support: harpinder.singh@rvsolutions.in</p>
</div>
""", unsafe_allow_html=True)