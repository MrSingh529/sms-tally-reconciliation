# chatbot.py (fixed)
import streamlit as st
import os
from typing import Dict, List, Optional
from datetime import datetime

class Chatbot:
    def __init__(self):
        self.chat_history_key = "chat_history"
        self.chat_open_key = "chat_open"
        self.chat_initialized_key = "chat_initialized"

        # Initialize session state
        if self.chat_history_key not in st.session_state:
            st.session_state[self.chat_history_key] = []

        if self.chat_open_key not in st.session_state:
            st.session_state[self.chat_open_key] = False

        if self.chat_initialized_key not in st.session_state:
            st.session_state[self.chat_initialized_key] = False

        # Conversation flows (unchanged)
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

        # Define file downloads (same as yours)
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

    # ---------------------------
    # Core chat helpers (unchanged)
    # ---------------------------
    def add_message(self, sender: str, message: str, is_option: bool = False):
        """Add a message to chat history"""
        st.session_state[self.chat_history_key].append({
            "sender": sender,
            "message": message,
            "time": datetime.now().strftime("%H:%M"),
            "is_option": is_option
        })

    def initialize_chat(self):
        """Initialize chat with greeting if not already done"""
        if not st.session_state[self.chat_initialized_key]:
            self.add_message("bot", self.flows["main_menu"]["message"])
            st.session_state[self.chat_initialized_key] = True

    def handle_option_click(self, option_action: str):
        """Handle option selection"""
        if option_action.startswith("download_"):
            # Handle downloads
            if option_action in self.download_files:
                file_info = self.download_files[option_action]
                self.add_message("user", f"Selected: {option_action.replace('_', ' ').title()}")
                self.add_message("bot", self.flows["download_success"]["message"])

                # Trigger download
                self.trigger_download(file_info)
            else:
                self.add_message("bot", "Download option not available yet.")
                self.show_main_menu()

        elif option_action == "main_menu":
            self.show_main_menu()

        elif option_action == "close_chat":
            st.session_state[self.chat_open_key] = False

        elif option_action in self.flows:
            # Show submenu
            flow = self.flows[option_action]
            self.add_message("bot", flow["message"])

    def show_main_menu(self):
        """Show main menu options"""
        self.add_message("bot", self.flows["main_menu"]["message"])

    def trigger_download(self, file_info: Dict):
        """Trigger file download"""
        st.session_state["trigger_download"] = {
            "filename": file_info["filename"],
            "url": file_info["url"],
            "local_path": file_info.get("local_path")
        }

    # ---------------------------
    # Rendering (safe, Streamlit-only)
    # ---------------------------
    def render_chat_interface(self):
        """Render the chat interface using Streamlit widgets only"""
        # Header block
        st.markdown("""
        <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 border-radius: 10px 10px 0 0; color: white; font-weight: 600; margin-bottom: 10px;">
            🤖 Reconciliation Assistant
        </div>
        """, unsafe_allow_html=True)

        # Messages area (scroll will be provided by Streamlit container)
        container = st.container()
        with container:
            for i, msg in enumerate(st.session_state[self.chat_history_key]):
                if msg["sender"] == "bot":
                    st.markdown(f"""
                    <div style="background: #f0f2f6; padding: 12px; border-radius: 12px; margin-bottom: 8px; max-width: 85%;">
                        <div style="font-weight: 600; color: #667eea; font-size: 0.9em;">Assistant</div>
                        <div style="margin-top: 6px;">{msg['message']}</div>
                        <div style="text-align: right; font-size: 0.8em; color: #718096; margin-top: 6px;">
                            {msg['time']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #667eea; color: white; padding: 12px; border-radius: 12px; margin-bottom: 8px; max-width: 85%; margin-left: auto;">
                        <div style="font-weight: 600; font-size: 0.9em;">You</div>
                        <div style="margin-top: 6px;">{msg['message']}</div>
                        <div style="text-align: right; font-size: 0.8em; opacity: 0.8; margin-top: 6px;">
                            {msg['time']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Show options for last bot message
        if st.session_state[self.chat_history_key]:
            last_msg = st.session_state[self.chat_history_key][-1]
            if last_msg["sender"] == "bot":
                # find flow by exact message (safe)
                current_flow = None
                for flow_name, flow in self.flows.items():
                    if flow["message"] == last_msg["message"]:
                        current_flow = flow
                        break

                if current_flow:
                    # Render option buttons (Streamlit buttons)
                    for option in current_flow.get("options", []):
                        # Use a callback wrapper to avoid passing strings
                        def make_callback(action):
                            return lambda: self._option_clicked(action)

                        # Unique key per message and option to avoid collision
                        key = f"opt_{len(st.session_state[self.chat_history_key])}_{option['action']}"
                        if st.button(option["text"], key=key, use_container_width=True):
                            # direct call - ensures callable, not string
                            self._option_clicked(option["action"])
                            st.experimental_rerun()

    def _option_clicked(self, action: str):
        """Internal handler used by button callbacks"""
        # Add a small user echo for UI clarity
        # (avoid adding huge strings)
        if action in self.download_files:
            # echo selected friendly text
            self.add_message("user", f"{action.replace('_', ' ').title()}")
        self.handle_option_click(action)

    def find_action_for_option(self, option_text: str) -> Optional[str]:
        """Find the action for a given option text"""
        for flow_name, flow in self.flows.items():
            for option in flow.get("options", []):
                if option["text"] == option_text:
                    return option["action"]
        return None

    def render_chat_button(self):
        """Render a safe floating-like chat button using Streamlit UI (no inline JS/onclick)"""
        # Place the button in the bottom-right using Streamlit layout columns
        cols = st.columns([1,1,1,1,1,1,6])
        # Put the button in the last narrow column to visually float it right
        with cols[-1]:
            # Use a simple Streamlit button - no HTML or JS
            if st.button("🤖 Chat", key="floating_chat_button_native"):
                # Toggle state using a callable, not a string
                st.session_state[self.chat_open_key] = not st.session_state.get(self.chat_open_key, False)
                if st.session_state[self.chat_open_key] and not st.session_state[self.chat_initialized_key]:
                    self.initialize_chat()
                # rerun to reflect UI changes immediately
                st.experimental_rerun()