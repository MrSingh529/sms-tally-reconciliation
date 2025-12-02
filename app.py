import streamlit as st
import pandas as pd
import tempfile
import os
import base64
from datetime import datetime
from automation import SMSTallyAutomation
import plotly.graph_objects as go
import plotly.express as px

# Function to load custom font
def load_font(font_path):
    with open(font_path, "rb") as f:
        font_data = f.read()
    font_b64 = base64.b64encode(font_data).decode()
    return font_b64

# Load your custom font (adjust path as needed)
FONT_PATH = "fonts/ClashGrotesk-Regular.ttf"
font_b64 = None
if os.path.exists(FONT_PATH):
    try:
        font_b64 = load_font(FONT_PATH)
    except Exception as e:
        st.warning(f"Could not load custom font: {e}")

# Page configuration
st.set_page_config(
    page_title="SMS & Tally Reconciliation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
if font_b64:
    font_import = f"""
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
    font_import = ""

custom_css = f"""
<style>
    {font_import}
    
    /* Modern color palette */
    :root {{
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Main container styling */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
    
    /* Hero section */
    .hero-section {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        text-align: center;
    }}
    
    .hero-title {{
        font-size: 3rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    
    .hero-subtitle {{
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
    }}
    
    /* Card styling */
    .upload-card {{
        background: var(--bg-card);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        height: 100%;
    }}
    
    .upload-card:hover {{
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }}
    
    .card-icon {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }}
    
    .card-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .card-description {{
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-light) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }}
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        padding: 0.5rem;
    }}
    
    /* File uploader */
    [data-testid="stFileUploader"] {{
        background: var(--bg-light);
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }}
    
    [data-testid="stFileUploader"]:hover {{
        border-color: var(--primary-color);
        background: white;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        background: transparent;
        border-bottom: 2px solid var(--border-color);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 3rem;
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0 2rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: var(--primary-color);
        color: white;
    }}
    
    /* Status badges */
    .status-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .status-success {{
        background: #d1fae5;
        color: #065f46;
    }}
    
    .status-warning {{
        background: #fef3c7;
        color: #92400e;
    }}
    
    /* Alert boxes */
    .custom-alert {{
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        font-weight: 500;
    }}
    
    .alert-success {{
        background: #d1fae5;
        border-color: var(--success-color);
        color: #065f46;
    }}
    
    .alert-info {{
        background: #dbeafe;
        border-color: var(--primary-color);
        color: #1e40af;
    }}
    
    .alert-warning {{
        background: #fef3c7;
        border-color: var(--warning-color);
        color: #92400e;
    }}
    
    /* Footer */
    .custom-footer {{
        text-align: center;
        padding: 2rem;
        margin-top: 4rem;
        border-top: 1px solid var(--border-color);
        background: var(--bg-light);
        border-radius: 12px;
    }}
    
    .footer-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .footer-text {{
        color: var(--text-secondary);
        font-size: 0.9rem;
    }}
    
    /* Progress indicator */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }}
    
    /* Data frame styling */
    .dataframe {{
        font-size: 0.875rem;
    }}
    
    /* Number input, select box */
    .stNumberInput, .stSelectbox {{
        background: white;
        border-radius: 8px;
    }}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📊 Reconciliation Hub</div>
    <div class="hero-subtitle">Intelligent SMS & Tally matching with GST verification</div>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    with st.expander("🎯 Matching Parameters", expanded=True):
        tolerance_days = st.number_input(
            "Date Tolerance (days)", 
            min_value=0, 
            max_value=365, 
            value=30,
            help="Maximum days difference for date matching"
        )
        
        tolerance_amount = st.number_input(
            "Amount Tolerance (₹)", 
            min_value=0.0, 
            value=0.0,
            step=0.1,
            help="Maximum amount difference for matching"
        )
    
    with st.expander("🔍 GST Verification", expanded=True):
        check_gst = st.checkbox(
            "Enable GST verification", 
            value=True,
            help="Verify service claims against GST files"
        )
    
    st.markdown("---")
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>📋 Quick Guide</strong><br>
        1️⃣ Upload SMS file<br>
        2️⃣ Upload Tally file<br>
        3️⃣ Add GST files (optional)<br>
        4️⃣ Process & download results
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Need help?**")
    st.markdown("📧 harpinder.singh@rvsolutions.in")

# File Upload Section
st.markdown("### 📤 Upload Your Files")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="upload-card">
        <span class="card-icon">💬</span>
        <div class="card-title">SMS Data</div>
        <div class="card-description">Upload your SMS transaction export file</div>
    </div>
    """, unsafe_allow_html=True)
    
    sms_file = st.file_uploader(
        "SMS File",
        type=['xlsx', 'xls', 'xlsm'],
        key="sms_uploader",
        label_visibility="collapsed"
    )
    if sms_file:
        st.success(f"✓ {sms_file.name}")

with col2:
    st.markdown("""
    <div class="upload-card">
        <span class="card-icon">📊</span>
        <div class="card-title">Tally Data</div>
        <div class="card-description">Upload your Tally export file</div>
    </div>
    """, unsafe_allow_html=True)
    
    tally_file = st.file_uploader(
        "Tally File",
        type=['xlsx', 'xls', 'xlsm'],
        key="tally_uploader",
        label_visibility="collapsed"
    )
    if tally_file:
        st.success(f"✓ {tally_file.name}")

with col3:
    st.markdown("""
    <div class="upload-card">
        <span class="card-icon">🧾</span>
        <div class="card-title">GST Files</div>
        <div class="card-description">Upload GST 2A/2B files (optional)</div>
    </div>
    """, unsafe_allow_html=True)
    
    gst_files = st.file_uploader(
        "GST Files",
        type=['xlsx', 'xls', 'xlsm'],
        accept_multiple_files=True,
        key="gst_uploader",
        label_visibility="collapsed"
    )
    if gst_files:
        st.success(f"✓ {len(gst_files)} file(s)")

st.markdown("<br>", unsafe_allow_html=True)

# Process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_btn = st.button("🚀 Start Processing", type="primary", use_container_width=True)

if process_btn:
    if sms_file and tally_file:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize
            status_text.text("🔧 Initializing...")
            progress_bar.progress(10)
            automation = SMSTallyAutomation(
                tolerance_days=tolerance_days,
                tolerance_amount=tolerance_amount
            )
            
            # Process SMS
            status_text.text("💬 Processing SMS data...")
            progress_bar.progress(25)
            sms_df = automation.read_excel_file(sms_file)
            sms_df = automation.process_sms_data(sms_df)
            
            # Process Tally
            status_text.text("📊 Processing Tally data...")
            progress_bar.progress(50)
            tally_df = automation.read_excel_file(tally_file)
            tally_df = automation.process_tally_data(tally_df)
            
            # Match data
            status_text.text("🔄 Matching records...")
            progress_bar.progress(75)
            sms_df, tally_df = automation.match_sms_tally_data(sms_df, tally_df)
            
            # GST verification
            if check_gst and gst_files:
                status_text.text("🔍 Verifying GST...")
                progress_bar.progress(90)
                sms_df = automation.check_gst_for_service_claims(sms_df, gst_files)
                tally_df = automation.check_gst_for_service_claims(tally_df, gst_files)
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            # Get statistics
            stats = automation.get_summary_stats(sms_df, tally_df)
            
            # Success message
            st.markdown("""
            <div class="custom-alert alert-success">
                <strong>✅ Processing Complete!</strong><br>
                Your data has been successfully reconciled.
            </div>
            """, unsafe_allow_html=True)
            
            # Summary Dashboard
            st.markdown("### 📈 Reconciliation Dashboard")
            
            # Create metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                match_rate_sms = (stats['matched_sms_count'] / (stats['matched_sms_count'] + stats['unmatched_sms_count']) * 100) if (stats['matched_sms_count'] + stats['unmatched_sms_count']) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{match_rate_sms:.1f}%</div>
                    <div class="metric-label">SMS Match Rate</div>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Matched", f"{stats['matched_sms_count']:,}", delta=f"{stats['unmatched_sms_count']:,} unmatched")
            
            with col2:
                match_rate_tally = (stats['matched_tally_count'] / (stats['matched_tally_count'] + stats['unmatched_tally_count']) * 100) if (stats['matched_tally_count'] + stats['unmatched_tally_count']) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{match_rate_tally:.1f}%</div>
                    <div class="metric-label">Tally Match Rate</div>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Matched", f"{stats['matched_tally_count']:,}", delta=f"{stats['unmatched_tally_count']:,} unmatched")
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">₹{stats['matched_sms_sum']:,.0f}</div>
                    <div class="metric-label">SMS Amount</div>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Total SMS", f"₹{stats['total_sms_sum']:,.2f}")
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">₹{stats['matched_tally_sum']:,.0f}</div>
                    <div class="metric-label">Tally Amount</div>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Total Tally", f"₹{stats['total_tally_sum']:,.2f}")
            
            # Warning for discrepancies
            if abs(stats['matched_sms_sum'] - stats['matched_tally_sum']) > 0.01:
                st.markdown("""
                <div class="custom-alert alert-warning">
                    ⚠️ <strong>Amount Mismatch Detected</strong><br>
                    The sum of matched SMS and Tally amounts differ. Please review the unmatched records.
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Results tabs
            tab1, tab2, tab3 = st.tabs(["📱 SMS Results", "📊 Tally Results", "📉 Analytics"])
            
            with tab1:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("#### SMS Transaction Records")
                with col2:
                    csv = sms_df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download CSV",
                        data=csv,
                        file_name=f"sms_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Clean display
                sms_display = sms_df.copy()
                for col in sms_display.columns:
                    if sms_display[col].dtype == 'object':
                        sms_display[col] = sms_display[col].astype(str)
                
                st.dataframe(sms_display, use_container_width=True, height=500)
            
            with tab2:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("#### Tally Transaction Records")
                with col2:
                    csv = tally_df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download CSV",
                        data=csv,
                        file_name=f"tally_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # Clean display
                tally_display = tally_df.copy()
                for col in tally_display.columns:
                    if tally_display[col].dtype == 'object':
                        tally_display[col] = tally_display[col].astype(str)
                
                st.dataframe(tally_display, use_container_width=True, height=500)
            
            with tab3:
                st.markdown("#### Reconciliation Analytics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # SMS Match pie chart
                    fig_sms = go.Figure(data=[go.Pie(
                        labels=['Matched', 'Unmatched'],
                        values=[stats['matched_sms_count'], stats['unmatched_sms_count']],
                        marker_colors=['#10b981', '#ef4444'],
                        hole=0.4
                    )])
                    fig_sms.update_layout(
                        title="SMS Records Status",
                        height=350,
                        showlegend=True
                    )
                    st.plotly_chart(fig_sms, use_container_width=True)
                
                with col2:
                    # Tally Match pie chart
                    fig_tally = go.Figure(data=[go.Pie(
                        labels=['Matched', 'Unmatched'],
                        values=[stats['matched_tally_count'], stats['unmatched_tally_count']],
                        marker_colors=['#10b981', '#ef4444'],
                        hole=0.4
                    )])
                    fig_tally.update_layout(
                        title="Tally Records Status",
                        height=350,
                        showlegend=True
                    )
                    st.plotly_chart(fig_tally, use_container_width=True)
                
                # Amount comparison
                fig_amount = go.Figure(data=[
                    go.Bar(name='SMS', x=['Matched', 'Total'], y=[stats['matched_sms_sum'], stats['total_sms_sum']], marker_color='#6366f1'),
                    go.Bar(name='Tally', x=['Matched', 'Total'], y=[stats['matched_tally_sum'], stats['total_tally_sum']], marker_color='#8b5cf6')
                ])
                fig_amount.update_layout(
                    title="Amount Comparison",
                    yaxis_title="Amount (₹)",
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig_amount, use_container_width=True)
            
            # GST Summary
            if check_gst and 'GST Status' in sms_df.columns:
                st.markdown("### 🧾 GST Verification Summary")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**SMS GST Status**")
                    gst_counts = sms_df['GST Status'].value_counts()
                    st.dataframe(gst_counts, use_container_width=True)
                
                with col2:
                    if 'GST Status' in tally_df.columns:
                        st.markdown("**Tally GST Status**")
                        gst_counts = tally_df['GST Status'].value_counts()
                        st.dataframe(gst_counts, use_container_width=True)
                
        except Exception as e:
            st.markdown(f"""
            <div class="custom-alert alert-warning">
                <strong>❌ Processing Error</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.exception(e)
    else:
        st.markdown("""
        <div class="custom-alert alert-warning">
            <strong>⚠️ Missing Files</strong><br>
            Please upload both SMS and Tally files to proceed with reconciliation.
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="custom-footer">
    <div class="footer-title">🚀 Embrace Automation</div>
    <div class="footer-text">
        Step into the future - Embrace learning over manual tasks<br>
        <strong>Harpinder Singh</strong> | RV Solutions<br>
        📧 harpinder.singh@rvsolutions.in
    </div>
</div>
""", unsafe_allow_html=True)