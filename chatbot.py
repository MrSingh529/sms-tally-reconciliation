# chatbot.py
import streamlit as st
import os
from typing import Dict, List, Optional
from datetime import datetime

class Chatbot:
    def __init__(self):
        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        if "chat_open" not in st.session_state:
            st.session_state.chat_open = False
        
        if "chat_initialized" not in st.session_state:
            st.session_state.chat_initialized = False
        
        if "current_flow" not in st.session_state:
            st.session_state.current_flow = "main_menu"
        
        # Define the conversation flow
        self.flows = {
            "main_menu": {
                "message": "Hello RVian! What do you want to do today?",
                "options": [
                    {"text": "Download Tally Template", "action": "download_tally"},
                    {"text": "Download SMS Template", "action": "download_sms"},
                    {"text": "Download GST Template", "action": "gst_submenu"},
                    {"text": "How to Run", "action": "how_to_run"},
                    {"text": "Things to Consider", "action": "things_to_consider"}
                ]
            },
            "gst_submenu": {
                "message": "Okay Here we go choose",
                "options": [
                    {"text": "Format 1", "action": "download_gst_format1"},
                    {"text": "Format 2", "action": "download_gst_format2"},
                    {"text": "← Back to Main Menu", "action": "main_menu"}
                ]
            },
            "how_to_run": {
                "message": """**How to Run the Reconciliation Suite:**

1. **Upload Files**: 
   - Upload SMS transaction data file
   - Upload Tally transaction data file
   - Optionally upload GST 2A/2B files for verification

2. **Configure Parameters**:
   - Set Date Tolerance (days)
   - Set Amount Tolerance (₹)
   - Enable/Disable GST verification

3. **Process**:
   - Click 'Start Reconciliation Process'
   - Wait for processing to complete
   - Review results and download reports

**Tips**:
- Ensure files are in Excel format (.xlsx, .xls, .xlsm)
- Check column names match expected formats
- Verify GST files contain invoice value columns""",
                "options": [
                    {"text": "← Back to Main Menu", "action": "main_menu"}
                ]
            },
            "things_to_consider": {
                "message": """**Important Things to Consider:**

✅ **Before Processing**:
1. Data Quality
   - Check for duplicate transactions
   - Verify date formats are consistent
   - Ensure amounts are numeric values

2. File Preparation
   - Remove any empty rows from files
   - Check column headers match expected names
   - Save files in Excel format before upload

3. GST Verification
   - Ensure GST files contain 'Invoice Value' column
   - Verify financial year matches transaction dates
   - Check for partial matches in GST data

⚠️ **Common Issues**:
- Date format mismatches
- Special characters in descriptions
- Missing transaction IDs
- Rounding differences in amounts

🔧 **Troubleshooting**:
1. If matching fails, reduce tolerance values
2. Check for hidden spaces in text columns
3. Verify file encoding (use UTF-8)
4. Ensure sufficient memory for large files""",
                "options": [
                    {"text": "← Back to Main Menu", "action": "main_menu"}
                ]
            },
            "download_success": {
                "message": "✅ Download initiated! Check your downloads folder.",
                "options": [
                    {"text": "Back to Main Menu", "action": "main_menu"},
                    {"text": "Close Chat", "action": "close_chat"}
                ]
            }
        }
        
        # Define file downloads
        self.download_files = {
            "download_tally": {
                "filename": "Tally_Template.xlsx",
                "url": "https://github.com/MrSingh529/sms-tally-reconciliation/raw/refs/heads/main/templates/Tally_Template.xlsx",
                "local_path": "templates/Tally_Template.xlsx"
            },
            "download_sms": {
                "filename": "SMS_Template.xlsx",
                "url": "https://github.com/MrSingh529/sms-tally-reconciliation/raw/refs/heads/main/templates/SMS_Template.xlsx",
                "local_path": "templates/SMS_Template.xlsx"
            },
            "download_gst_format1": {
                "filename": "GST_Template_Format1.xlsx",
                "url": "https://github.com/MrSingh529/sms-tally-reconciliation/raw/refs/heads/main/templates/GST_Format1.xls",
                "local_path": "templates/GST_Format1.xlsx"
            },
            "download_gst_format2": {
                "filename": "GST_Template_Format2.xlsx",
                "url": "https://github.com/MrSingh529/sms-tally-reconciliation/raw/refs/heads/main/templates/GST_Format2.xlsx",
                "local_path": "templates/GST_Format2.xlsx"
            }
        }
    
    def add_message(self, sender: str, message: str):
        """Add a message to chat history"""
        st.session_state.chat_history.append({
            "sender": sender,
            "message": message,
            "time": datetime.now().strftime("%H:%M")
        })
    
    def initialize_chat(self):
        """Initialize chat with greeting if not already done"""
        if not st.session_state.chat_initialized:
            self.add_message("bot", self.flows["main_menu"]["message"])
            st.session_state.chat_initialized = True
    
    def handle_option(self, option_action: str):
        """Handle option selection"""
        if option_action.startswith("download_"):
            # Handle downloads
            if option_action in self.download_files:
                file_info = self.download_files[option_action]
                self.add_message("user", f"Selected: {option_action.replace('_', ' ').title()}")
                self.add_message("bot", self.flows["download_success"]["message"])
                st.session_state.current_flow = "download_success"
                
                # Trigger download
                st.session_state["trigger_download"] = {
                    "filename": file_info["filename"],
                    "local_path": file_info.get("local_path")
                }
            else:
                self.add_message("bot", "Download option not available yet.")
                self.show_main_menu()
        
        elif option_action == "main_menu":
            self.show_main_menu()
        
        elif option_action == "close_chat":
            st.session_state.chat_open = False
        
        elif option_action in self.flows:
            # Show submenu
            self.add_message("user", f"Selected: {option_action.replace('_', ' ').title()}")
            self.add_message("bot", self.flows[option_action]["message"])
            st.session_state.current_flow = option_action
    
    def show_main_menu(self):
        """Show main menu options"""
        self.add_message("bot", self.flows["main_menu"]["message"])
        st.session_state.current_flow = "main_menu"
    
    def render_chat_interface(self):
        """Render the chat interface"""
        # Create a container for the chat
        with st.container():
            # Chat header
            st.markdown("""
            <div style="padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; font-weight: 600; border-radius: 10px 10px 0 0; margin-bottom: 10px;">
                🤖 Reconciliation Assistant
            </div>
            """, unsafe_allow_html=True)
            
            # Chat messages area
            chat_container = st.container(height=350)
            
            with chat_container:
                # Display chat history
                for msg in st.session_state.chat_history:
                    if msg["sender"] == "bot":
                        st.markdown(f"""
                        <div style="background: #f0f2f6; padding: 12px; border-radius: 15px; 
                                 margin-bottom: 10px; max-width: 85%;">
                            <div style="font-weight: 600; color: #667eea; font-size: 0.9em;">Assistant</div>
                            <div style="margin-top: 5px;">{msg['message']}</div>
                            <div style="text-align: right; font-size: 0.8em; color: #718096; margin-top: 5px;">
                                {msg['time']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    elif msg["sender"] == "user":
                        st.markdown(f"""
                        <div style="background: #667eea; color: white; padding: 12px; border-radius: 15px; 
                                 margin-bottom: 10px; max-width: 85%; margin-left: auto;">
                            <div style="font-weight: 600; font-size: 0.9em;">You</div>
                            <div style="margin-top: 5px;">{msg['message']}</div>
                            <div style="text-align: right; font-size: 0.8em; opacity: 0.8; margin-top: 5px;">
                                {msg['time']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show options for current flow
            current_flow = st.session_state.current_flow
            if current_flow in self.flows:
                options = self.flows[current_flow]["options"]
                
                # Create options as Streamlit buttons
                for option in options:
                    if st.button(
                        option["text"],
                        key=f"chat_option_{option['action']}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        self.handle_option(option["action"])
                        st.rerun()
    
    def render_chat_button(self):
        """Render the floating chat button"""
        # Use HTML/CSS for fixed positioning
        st.markdown("""
        <style>
        .floating-chat-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create a container for the button
        with st.container():
            st.markdown('<div class="floating-chat-btn">', unsafe_allow_html=True)
            
            # Create the actual Streamlit button
            if st.button(
                "🤖",
                key="chat_toggle_button",
                help="Chat with Assistant"
            ):
                st.session_state.chat_open = not st.session_state.chat_open
                if st.session_state.chat_open and not st.session_state.chat_initialized:
                    self.initialize_chat()
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)