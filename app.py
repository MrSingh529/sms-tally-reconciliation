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
    page_title="SMS & Tally Reconciliation Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design
if font_b64:
    custom_css = f"""
    <style>
        @font-face {{
            font-family: 'ClashGrotesk';
            src: url(data:font/ttf;base64,{font_b64}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        
        * {{
            font-family: 'ClashGrotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }}
        
        /* Modern gradient background */
        .stApp {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        /* Main content container */
        .main .block-container {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-top: 2rem;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Header styling */
        .main-header {{
            font-family: 'ClashGrotesk', sans-serif;
            font-size: 3rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 0.5rem;
            font-weight: 700;
            letter-spacing: -1px;
        }}
        
        .sub-header {{
            font-family: 'ClashGrotesk', sans-serif;
            font-size: 1.1rem;
            color: #6b7280;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 400;
        }}
        
        /* Enhanced metric cards */
        [data-testid="stMetricValue"] {{
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }}
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 20px;
            border: 2px dashed #667eea;
            transition: all 0.3s ease;
        }}
        
        [data-testid="stFileUploader"]:hover {{
            border-color: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }}
        
        /* Button styling */
        .stButton > button {{
            font-family: 'ClashGrotesk', sans-serif;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 32px;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }}
        
        /* Download button styling */
        .stDownloadButton > button {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stDownloadButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(86, 171, 47, 0.4);
        }}
        
        /* Status cards */
        .status-card {{
            background: white;
            border-radius: 15px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-left: 5px solid #667eea;
            margin: 15px 0;
            transition: all 0.3s ease;
        }}
        
        .status-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}
        
        .success-card {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 5px solid #28a745;
        }}
        
        .warning-card {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            border-left: 5px solid #ffc107;
        }}
        
        .info-card {{
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border-left: 5px solid #17a2b8;
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 5px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        /* DataFrames */
        [data-testid="stDataFrame"] {{
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        /* Info boxes */
        .info-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #2196f3;
        }}
        
        /* Progress indicators */
        .stProgress > div > div {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }}
        
        /* Sidebar elements */
        [data-testid="stSidebar"] .stNumberInput input,
        [data-testid="stSidebar"] .stCheckbox {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            margin-top: 40px;
        }}
        
        /* Animation for success */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .animate-in {{
            animation: slideIn 0.5s ease-out;
        }}
    </style>
    """
else:
    # Simplified fallback CSS
    custom_css = """
    <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .main .block-container {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .main-header {
            font-size: 3rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-weight: 700;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            padding: 12px 32px;
            font-weight: 600;
        }
    </style>
    """

st.markdown(custom_css, unsafe_allow_html=True)

# Header with icon
st.markdown('''
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
        <h1 class="main-header">SMS & Tally Reconciliation Pro</h1>
        <p class="sub-header">Intelligent matching with GST verification powered by automation</p>
    </div>
''', unsafe_allow_html=True)

# Sidebar with enhanced design
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    with st.expander("📅 Matching Parameters", expanded=True):
        tolerance_days = st.number_input(
            "Date Tolerance (Days)", 
            min_value=0, 
            max_value=365, 
            value=30,
            help="Maximum days difference for matching records"
        )
        
        tolerance_amount = st.number_input(
            "Amount Tolerance (₹)", 
            min_value=0.0, 
            value=0.0,
            step=0.1,
            format="%.2f",
            help="Maximum amount difference for matching"
        )
    
    with st.expander("🔍 GST Verification", expanded=True):
        check_gst = st.checkbox(
            "Enable GST Verification", 
            value=True,
            help="Verify service claims against GST files"
        )
    
    st.markdown("---")
    
    st.markdown("""
    <div class="info-box">
        <h4 style="margin-top: 0;">📋 Quick Guide</h4>
        <ol style="padding-left: 20px;">
            <li>Upload SMS Excel file</li>
            <li>Upload Tally Excel file</li>
            <li>Add GST files (optional)</li>
            <li>Configure parameters</li>
            <li>Click Process & Download</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Main content with enhanced cards
st.markdown("### 📤 Upload Your Files")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="status-card">
        <h4 style="color: #667eea; margin-top: 0;">📱 SMS Data</h4>
        <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem;">
            Required: TransactionDate, TransactionMode, Description, Remarks, Debit, Credit
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sms_file = st.file_uploader(
        "Drop SMS file here",
        type=['xlsx', 'xls', 'xlsm'],
        key="sms_uploader",
        label_visibility="collapsed"
    )
    if sms_file:
        st.success(f"✓ {sms_file.name} uploaded")

with col2:
    st.markdown("""
    <div class="status-card">
        <h4 style="color: #764ba2; margin-top: 0;">📚 Tally Data</h4>
        <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem;">
            Required: Date, Particulars, Vch Type, Vch No., Debit, Credit
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tally_file = st.file_uploader(
        "Drop Tally file here",
        type=['xlsx', 'xls', 'xlsm'],
        key="tally_uploader",
        label_visibility="collapsed"
    )
    if tally_file:
        st.success(f"✓ {tally_file.name} uploaded")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="status-card info-card">
    <h4 style="margin-top: 0;">📋 GST Files (Optional)</h4>
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
        Upload GST 2A/2B files for invoice verification
    </p>
</div>
""", unsafe_allow_html=True)

gst_files = st.file_uploader(
    "Drop GST files here",
    type=['xlsx', 'xls', 'xlsm'], 
    accept_multiple_files=True,
    key="gst_uploader",
    label_visibility="collapsed"
)
if gst_files:
    st.success(f"✓ {len(gst_files)} GST file(s) uploaded")

st.markdown("<br>", unsafe_allow_html=True)

# Process button with enhanced styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button("🚀 Process & Match Data", type="primary", use_container_width=True)

if process_button:
    if sms_file and tally_file:
        with st.spinner("🔄 Processing your data... Please wait"):
            progress_bar = st.progress(0)
            
            try:
                # Initialize automation
                automation = SMSTallyAutomation(
                    tolerance_days=tolerance_days,
                    tolerance_amount=tolerance_amount
                )
                progress_bar.progress(10)
                
                # Process SMS data
                sms_df = automation.read_excel_file(sms_file)
                sms_df = automation.process_sms_data(sms_df)
                progress_bar.progress(30)
                
                # Process Tally data
                tally_df = automation.read_excel_file(tally_file)
                tally_df = automation.process_tally_data(tally_df)
                progress_bar.progress(50)
                
                # Match data
                sms_df, tally_df = automation.match_sms_tally_data(sms_df, tally_df)
                progress_bar.progress(70)
                
                # Check GST if enabled
                if check_gst and gst_files:
                    sms_df = automation.check_gst_for_service_claims(sms_df, gst_files)
                    tally_df = automation.check_gst_for_service_claims(tally_df, gst_files)
                progress_bar.progress(90)
                
                # Get summary statistics
                stats = automation.get_summary_stats(sms_df, tally_df)
                progress_bar.progress(100)
                
                # Success message
                st.markdown("""
                <div class="status-card success-card animate-in">
                    <h3 style="margin-top: 0;">✅ Processing Complete!</h3>
                    <p>Your data has been successfully matched and reconciled.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display summary statistics with visual metrics
                st.markdown("### 📊 Reconciliation Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "✅ Matched SMS", 
                        f"{stats['matched_sms_count']:,}",
                        delta=f"{(stats['matched_sms_count']/stats['total_sms_sum']*100):.1f}%" if stats['total_sms_sum'] > 0 else "0%"
                    )
                    st.metric(
                        "❌ Unmatched SMS", 
                        f"{stats['unmatched_sms_count']:,}"
                    )
                
                with col2:
                    st.metric(
                        "✅ Matched Tally", 
                        f"{stats['matched_tally_count']:,}",
                        delta=f"{(stats['matched_tally_count']/stats['total_tally_sum']*100):.1f}%" if stats['total_tally_sum'] > 0 else "0%"
                    )
                    st.metric(
                        "❌ Unmatched Tally", 
                        f"{stats['unmatched_tally_count']:,}"
                    )
                
                with col3:
                    st.metric("💰 Matched SMS", f"₹{stats['matched_sms_sum']:,.2f}")
                    st.metric("📊 Total SMS", f"₹{stats['total_sms_sum']:,.2f}")
                
                with col4:
                    st.metric("💰 Matched Tally", f"₹{stats['matched_tally_sum']:,.2f}")
                    st.metric("📊 Total Tally", f"₹{stats['total_tally_sum']:,.2f}")
                
                # Visual representation
                if stats['matched_sms_count'] > 0 or stats['unmatched_sms_count'] > 0:
                    st.markdown("### 📈 Visual Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # SMS matching pie chart
                        fig1 = go.Figure(data=[go.Pie(
                            labels=['Matched', 'Unmatched'],
                            values=[stats['matched_sms_count'], stats['unmatched_sms_count']],
                            hole=.4,
                            marker_colors=['#28a745', '#dc3545']
                        )])
                        fig1.update_layout(
                            title="SMS Matching Status",
                            showlegend=True,
                            height=300
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        # Tally matching pie chart
                        fig2 = go.Figure(data=[go.Pie(
                            labels=['Matched', 'Unmatched'],
                            values=[stats['matched_tally_count'], stats['unmatched_tally_count']],
                            hole=.4,
                            marker_colors=['#667eea', '#ffc107']
                        )])
                        fig2.update_layout(
                            title="Tally Matching Status",
                            showlegend=True,
                            height=300
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Check for discrepancies
                if abs(stats['matched_sms_sum'] - stats['matched_tally_sum']) > 0.01:
                    st.markdown("""
                    <div class="status-card warning-card">
                        <h4 style="margin-top: 0;">⚠️ Amount Mismatch Detected</h4>
                        <p>The sum of matched SMS and Tally records differs. Please review the data.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Results tabs with enhanced design
                tab1, tab2, tab3 = st.tabs(["📱 SMS Results", "📚 Tally Results", "📊 Analytics"])
                
                with tab1:
                    st.markdown("#### SMS Transaction Details")
                    
                    matched_count = len(sms_df[sms_df['Status'] == 'Tallied'])
                    unmatched_count = len(sms_df[sms_df['Status'] == 'Not Tallied'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"✅ **Matched:** {matched_count} records")
                    with col2:
                        st.warning(f"❌ **Unmatched:** {unmatched_count} records")
                    
                    # Display data
                    sms_display = sms_df.copy()
                    for col in sms_display.columns:
                        if sms_display[col].dtype == 'object':
                            sms_display[col] = sms_display[col].astype(str)
                    
                    st.dataframe(sms_display, use_container_width=True, height=400)
                    
                    # Download button
                    csv = sms_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download SMS Results",
                        data=csv,
                        file_name=f"sms_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with tab2:
                    st.markdown("#### Tally Transaction Details")
                    
                    matched_count = len(tally_df[tally_df['Status'] == 'Tallied'])
                    unmatched_count = len(tally_df[tally_df['Status'] == 'Not Tallied'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"✅ **Matched:** {matched_count} records")
                    with col2:
                        st.warning(f"❌ **Unmatched:** {unmatched_count} records")
                    
                    # Display data
                    tally_display = tally_df.copy()
                    for col in tally_display.columns:
                        if tally_display[col].dtype == 'object':
                            tally_display[col] = tally_display[col].astype(str)
                    
                    st.dataframe(tally_display, use_container_width=True, height=400)
                    
                    # Download button
                    csv = tally_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Tally Results",
                        data=csv,
                        file_name=f"tally_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with tab3:
                    st.markdown("#### Detailed Analytics")
                    
                    if check_gst and 'GST Status' in sms_df.columns:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**SMS GST Verification**")
                            gst_counts = sms_df['GST Status'].value_counts()
                            st.bar_chart(gst_counts)
                        
                        with col2:
                            st.markdown("**Tally GST Verification**")
                            if 'GST Status' in tally_df.columns:
                                gst_counts = tally_df['GST Status'].value_counts()
                                st.bar_chart(gst_counts)
                    
                    # Additional insights
                    st.markdown("**Matching Summary**")
                    summary_data = {
                        'Category': ['SMS Matched', 'SMS Unmatched', 'Tally Matched', 'Tally Unmatched'],
                        'Count': [
                            stats['matched_sms_count'],
                            stats['unmatched_sms_count'],
                            stats['matched_tally_count'],
                            stats['unmatched_tally_count']
                        ],
                        'Amount': [
                            stats['matched_sms_sum'],
                            stats['total_sms_sum'] - stats['matched_sms_sum'],
                            stats['matched_tally_sum'],
                            stats['total_tally_sum'] - stats['matched_tally_sum']
                        ]
                    }
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
                
            except Exception as e:
                st.markdown(f"""
                <div class="status-card warning-card">
                    <h4 style="margin-top: 0;">❌ Processing Error</h4>
                    <p>{str(e)}</p>
                </div>
                """, unsafe_allow_html=True)
                st.exception(e)
    else:
        st.markdown("""
        <div class="status-card warning-card">
            <h4 style="margin-top: 0;">⚠️ Missing Files</h4>
            <p>Please upload both SMS and Tally files to proceed with reconciliation.</p>
        </div>
        """, unsafe_allow_html=True)

# Enhanced footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <h3 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem;">
        Step Into The Future
    </h3>
    <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 0.5rem;">
        Embrace learning over manual tasks
    </p>
    <p style="color: #374151; font-weight: 600; font-size: 1.2rem; margin-bottom: 1.5rem;">
        Embrace Automation - Harpinder Singh
    </p>
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; padding: 15px; display: inline-block;">
        <p style="margin: 0; font-weight: 600;">
            📧 Support: harpinder.singh@rvsolutions.in
        </p>
    </div>
</div>
""", unsafe_allow_html=True)