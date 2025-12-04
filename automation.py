# automation.py
import pandas as pd
import numpy as np
import configparser
import os
import re
from fuzzywuzzy import fuzz

class SMSTallyAutomation:
    def __init__(self, tolerance_days=30, tolerance_amount=0.0):
        self.tolerance_days = tolerance_days
        self.tolerance_amount = tolerance_amount
    
    def read_excel_file(self, file):
        """Read Excel file from bytes or path"""
        if hasattr(file, 'read'):
            # If it's a file-like object (from Streamlit upload)
            return pd.read_excel(file)
        else:
            # If it's a file path
            return pd.read_excel(file)
    
    def process_sms_data(self, df):
        # Check if PaymentMode column exists, if not use Transaction Type
        if 'PaymentMode' in df.columns:
            df['Transaction Type'] = df['PaymentMode']
        elif 'Transaction Type' in df.columns:
            # Keep existing Transaction Type if PaymentMode doesn't exist
            pass
        else:
            # If neither exists, mark as Others
            df['Transaction Type'] = 'Others'
        
        expected_columns = ['TransactionDate', 'TransactionMode', 'Description', 'Remarks', 'Debit', 'Credit']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None  # Add missing columns to avoid KeyErrors

        df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], errors='coerce')
        
        df['Amount'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0) - pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        
        df['NormalizedID'] = df['Description'].astype(str).str.upper().str.replace('[^A-Z0-9]', '')
        
        df['Status'] = 'Not Tallied'
        df['GST Status'] = 'Not Checked'

        # Normalize formatting for relevant columns
        df['Description'] = df['Description'].str.strip().str.upper()
        df['TransactionMode'] = df['TransactionMode'].str.strip().str.upper()
        df['Amount'] = df['Amount'].round(2)  # Round to 2 decimal places
        df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], errors='coerce')
        df['Description'] = df['Description'].astype(str).str.upper()
        df['Remarks'] = df['Remarks'].astype(str).str.upper()
        df['Transaction Type'] = df['Transaction Type'].astype(str).str.upper()

        return df
    
    def process_tally_data(self, df):
        date_row_index = df.index[df.iloc[:, 0].astype(str).str.contains('Date', case=False, na=False)].tolist()

        if date_row_index:
            header_row = date_row_index[0]
            df.columns = df.iloc[header_row].fillna('')  # Replace NaNs in header row with empty strings        
            df = df.iloc[header_row + 1:].reset_index(drop=True)
        else:
            # If no date header found, assume first row is header
            pass

        df.columns = df.columns.str.strip()

        # Handle unexpected columns
        column_renames = {
            'TallyNote': 'Notes',
            'Voucher Type': 'Vch Type',
            'Voucher No': 'Vch No.',
            'Voucher No.': 'Vch No.',
            'Vch No': 'Vch No.',
        }
        
        for old_col, new_col in column_renames.items():
            if old_col in df.columns and new_col not in df.columns:
                df = df.rename(columns={old_col: new_col})
    
        required_columns = ['Date', 'Particulars', 'Vch Type', 'Vch No.', 'Debit', 'Credit']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None  # Add missing columns to avoid KeyErrors

        # Use Vch Type as Transaction Type
        df['Transaction Type'] = df['Vch Type']

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        df['Amount'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0) - pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        
        df['NormalizedID'] = df['Vch No.'].astype(str).str.upper().str.replace('[^A-Z0-9]', '')
        
        df['Status'] = 'Not Tallied'
        df['GST Status'] = 'Not Checked'
        
        df['Amount'] = df['Amount'].round(2)  # Round to 2 decimal places
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Vch No.'] = df['Vch No.'].astype(str).str.upper()
        df['Transaction Type'] = df['Transaction Type'].astype(str).str.upper()

        return df
    
    def match_sms_tally_data(self, sms_df, tally_df):
        matched_sms_indices = set()
        matched_tally_indices = set()

        # Add columns to track whether transaction is Debit or Credit
        sms_df['TransactionDirection'] = sms_df.apply(
            lambda row: 'Credit' if pd.notna(row.get('Credit')) and float(row.get('Credit', 0)) != 0 
            else 'Debit' if pd.notna(row.get('Debit')) and float(row.get('Debit', 0)) != 0 
            else 'Unknown', axis=1
        )
        
        tally_df['TransactionDirection'] = tally_df.apply(
            lambda row: 'Credit' if pd.notna(row.get('Credit')) and float(row.get('Credit', 0)) != 0 
            else 'Debit' if pd.notna(row.get('Debit')) and float(row.get('Debit', 0)) != 0 
            else 'Unknown', axis=1
        )

        # Convert to datetime for proper comparison
        sms_df['TransactionDate'] = pd.to_datetime(sms_df['TransactionDate'], errors='coerce')
        tally_df['Date'] = pd.to_datetime(tally_df['Date'], errors='coerce')
        
        # Round amounts for consistent comparison
        sms_df['Amount'] = sms_df['Amount'].round(2)
        tally_df['Amount'] = tally_df['Amount'].round(2)

        # First, try to match exact amount + date within tolerance + same direction
        for idx, tally_row in tally_df.iterrows():
            if idx in matched_tally_indices:
                continue
                
            # Check if we have valid data for matching
            if pd.isna(tally_row['Date']) or pd.isna(tally_row['Amount']):
                continue
                
            # Define date range for tolerance
            min_date = tally_row['Date'] - pd.Timedelta(days=self.tolerance_days)
            max_date = tally_row['Date'] + pd.Timedelta(days=self.tolerance_days)
            
            # Find SMS transactions that are:
            # 1. Within date tolerance
            # 2. Amount matches (within tolerance_amount)
            # 3. Same transaction direction (Credit-Credit or Debit-Debit)
            # 4. Not already matched
            potential_matches = sms_df[
                (sms_df['Status'] == 'Not Tallied') &
                (sms_df['TransactionDate'].between(min_date, max_date, inclusive='both')) &
                (abs(sms_df['Amount'] - tally_row['Amount']) <= self.tolerance_amount) &
                (sms_df['TransactionDirection'] == tally_row['TransactionDirection']) &
                (sms_df['TransactionDirection'] != 'Unknown')
            ]
            
            if not potential_matches.empty:
                # If multiple matches found, pick the one with closest date
                potential_matches = potential_matches.copy()
                potential_matches['DateDiff'] = abs((potential_matches['TransactionDate'] - tally_row['Date']).dt.days)
                best_match_idx = potential_matches['DateDiff'].idxmin()
                best_match = sms_df.loc[best_match_idx]
                
                # Mark as tallied
                sms_df.at[best_match_idx, 'Status'] = 'Tallied'
                tally_df.at[idx, 'Status'] = 'Tallied'
                
                # Add remarks about the match
                sms_df.at[best_match_idx, 'MatchRemarks'] = f"Matched with Tally: Amount {tally_row['Amount']}, Date {tally_row['Date'].strftime('%d-%b-%Y')}"
                tally_df.at[idx, 'MatchRemarks'] = f"Matched with SMS: Amount {best_match['Amount']}, Date {best_match['TransactionDate'].strftime('%d-%b-%Y')}"
                
                matched_sms_indices.add(best_match_idx)
                matched_tally_indices.add(idx)
                continue
            
            # Second Priority: Existing logic with scoring (for non-direct matches)
            # This includes cases where direction doesn't match or we need fuzzy matching
            if self.tolerance_amount > 0:  # Only if tolerance is allowed
                fuzzy_matches = sms_df[
                    (sms_df['Status'] == 'Not Tallied') &
                    (sms_df['TransactionDate'].between(min_date, max_date, inclusive='both')) &
                    (abs(sms_df['Amount'] - tally_row['Amount']) <= self.tolerance_amount)
                ]
                
                if not fuzzy_matches.empty:
                    best_match = None
                    highest_score = 0
                    
                    for _, sms_row in fuzzy_matches.iterrows():
                        score = self.calculate_match_score(tally_row, sms_row)
                        
                        # Bonus for same transaction direction
                        if sms_row['TransactionDirection'] == tally_row['TransactionDirection']:
                            score += 20
                        
                        if score > highest_score:
                            highest_score = score
                            best_match = sms_row
                    
                    if best_match is not None and highest_score > 30:  # Threshold for matching
                        self.mark_as_tallied(tally_row, best_match, sms_df, tally_df, 
                                        matched_sms_indices, matched_tally_indices)

        # Handle split transactions (combining multiple SMS transactions into one Tally entry)
        self.handle_split_transactions(sms_df, tally_df, matched_sms_indices, matched_tally_indices)

        # Mark remaining records as 'Not Tallied'
        sms_df.loc[~sms_df.index.isin(matched_sms_indices), 'Status'] = 'Not Tallied'
        tally_df.loc[~tally_df.index.isin(matched_tally_indices), 'Status'] = 'Not Tallied'

        return sms_df, tally_df
    
    def calculate_match_score(self, tally_row, sms_row):
        score = 0
        
        # Bonus for same transaction direction
        if sms_row['TransactionDirection'] == tally_row['TransactionDirection']:
            score += 20
        
        # Original scoring logic
        if pd.notna(tally_row['Vch No.']) and tally_row['Vch No.'] != "NAN":
            if tally_row['Vch No.'] in str(sms_row['Description']) or tally_row['Vch No.'] in str(sms_row['Remarks']):
                score += 50
            else:
                score += fuzz.partial_ratio(str(tally_row['Vch No.']), str(sms_row['Description'])) * 0.3
                score += fuzz.partial_ratio(str(tally_row['Vch No.']), str(sms_row['Remarks'])) * 0.2
        
        if tally_row['Transaction Type'] == sms_row['Transaction Type']:
            score += 30
        
        return score
    
    def handle_split_transactions(self, sms_df, tally_df, matched_sms_indices, matched_tally_indices):
        unmatched_tally = tally_df[~tally_df.index.isin(matched_tally_indices)]
        for idx, tally_row in unmatched_tally.iterrows():
            potential_splits = sms_df[
                (sms_df['TransactionDate'] == tally_row['Date']) &
                (~sms_df.index.isin(matched_sms_indices)) &
                (sms_df['Transaction Type'] == tally_row['Transaction Type'])
            ]
            
            if not potential_splits.empty and abs(potential_splits['Amount'].sum() - tally_row['Amount']) <= self.tolerance_amount:
                tally_df.at[idx, 'Status'] = 'Tallied'
                matched_tally_indices.add(idx)
                for split_idx in potential_splits.index:
                    sms_df.at[split_idx, 'Status'] = 'Tallied'
                    matched_sms_indices.add(split_idx)
    
    def mark_as_tallied(self, tally_row, sms_row, sms_df, tally_df, matched_sms_indices, matched_tally_indices):
        sms_df_index = sms_row.name
        tally_df_index = tally_row.name

        # Mark both as 'Tallied'
        sms_df.at[sms_df_index, 'Status'] = 'Tallied'
        tally_df.at[tally_df_index, 'Status'] = 'Tallied'
        
        # Add matching details
        date_diff = abs((sms_row['TransactionDate'] - tally_row['Date']).days)
        direction = "same" if sms_row['TransactionDirection'] == tally_row['TransactionDirection'] else "different"
        
        sms_df.at[sms_df_index, 'MatchDetails'] = f"Amount: {tally_row['Amount']}, Date diff: {date_diff} days, Direction: {direction}"
        tally_df.at[tally_df_index, 'MatchDetails'] = f"Amount: {sms_row['Amount']}, Date diff: {date_diff} days, Direction: {direction}"

        matched_sms_indices.add(sms_df_index)
        matched_tally_indices.add(tally_df_index)
    
    def check_gst_for_service_claims(self, df, gst_files):
        """Check GST files for service claim transactions"""
        if not gst_files:
            return df
        
        # Filter service claims
        service_claims = df[df['Transaction Type'].str.contains('SERVICE', case=False, na=False) | 
                           df['Transaction Type'].str.contains('CLAIM', case=False, na=False)]
        
        if service_claims.empty:
            return df
        
        # Load all GST files once and cache them
        gst_data_cache = []
        for gst_file in gst_files:
            try:
                gst_df = self.read_excel_file(gst_file)
                # Pre-process GST data for faster searching
                processed_gst = self.preprocess_gst_data(gst_df, gst_file)
                if processed_gst:
                    gst_data_cache.append(processed_gst)
            except Exception as e:
                continue
        
        if not gst_data_cache:
            return df
        
        # Process each service claim
        for idx, row in service_claims.iterrows():
            amount = row['Amount']
            date = row['TransactionDate'] if 'TransactionDate' in row else row['Date']
            year = date.year if pd.notna(date) else None
            
            if pd.isna(amount) or year is None:
                df.at[idx, 'GST Status'] = "Invalid Date/Amount"
                continue
            
            found_in_gst = False
            gst_year = None
            
            # Check all cached GST data
            for gst_data in gst_data_cache:
                gst_amount_found, found_year = self.check_cached_gst_data(gst_data, amount, year)
                if gst_amount_found:
                    found_in_gst = True
                    gst_year = found_year
                    break
            
            if found_in_gst and gst_year:
                df.at[idx, 'GST Status'] = f"Found in GST {gst_year}"
            else:
                df.at[idx, 'GST Status'] = "Not Found in GST"
        
        return df
    
    def preprocess_gst_data(self, gst_df, file):
        """Preprocess GST data for faster searching"""
        try:
            # Find amount column
            amount_col = None
            possible_amount_cols = ['INVOICE VALUE', 'INVOICE VALUE(₹)', 'Invoice Value', 
                                   'Invoice Value(₹)', 'Invoice Value (₹)', 'InvoiceValue']
            for col in gst_df.columns:
                for possible_col in possible_amount_cols:
                    if possible_col.upper() in col.upper():
                        amount_col = col
                        break
                if amount_col:
                    break
            
            if not amount_col:
                return None
            
            # Find date column
            date_col = None
            for col in gst_df.columns:
                col_lower = col.lower()
                if 'date' in col_lower:
                    date_col = col
                    break
            
            # Convert amount to numeric
            gst_df[amount_col] = pd.to_numeric(gst_df[amount_col], errors='coerce')
            
            # Extract year from date column if available - handle multiple date formats
            if date_col and date_col in gst_df.columns:
                try:
                    # Try with dayfirst=True for dd/mm/yyyy format
                    gst_df['Year'] = pd.to_datetime(gst_df[date_col], errors='coerce', dayfirst=True).dt.year
                except:
                    # If that fails, try without dayfirst
                    try:
                        gst_df['Year'] = pd.to_datetime(gst_df[date_col], errors='coerce').dt.year
                    except:
                        gst_df['Year'] = None
            else:
                # Try to extract year from filename
                if hasattr(file, 'name'):
                    filename = file.name
                else:
                    filename = str(file)
                year_match = re.search(r'(\d{2})-(\d{2})', filename)
                if year_match:
                    year1, year2 = year_match.groups()
                    gst_df['Year'] = int(f"20{year1}")  # Assuming 20xx format
                else:
                    gst_df['Year'] = None
            
            return {
                'data': gst_df,
                'amount_col': amount_col,
                'date_col': date_col
            }
        except Exception as e:
            return None
    
    def check_cached_gst_data(self, gst_data, amount, year):
        """Check cached GST data for matching amount and year"""
        gst_df = gst_data['data']
        amount_col = gst_data['amount_col']
        
        if amount_col not in gst_df.columns:
            return False, None
        
        # Check if amount matches
        if 'Year' in gst_df.columns and gst_df['Year'].notna().any():
            # Filter by year first for faster matching
            year_matches = gst_df[gst_df['Year'] == year]
            if not year_matches.empty:
                amount_matches = year_matches[abs(year_matches[amount_col] - amount) <= self.tolerance_amount]
            else:
                amount_matches = gst_df[abs(gst_df[amount_col] - amount) <= self.tolerance_amount]
        else:
            amount_matches = gst_df[abs(gst_df[amount_col] - amount) <= self.tolerance_amount]
        
        if not amount_matches.empty:
            return True, year
        
        return False, None
    
    def get_summary_stats(self, sms_df, tally_df):
        """Get summary statistics for display"""
        matched_sms = sms_df[sms_df['Status'] == 'Tallied']
        matched_tally = tally_df[tally_df['Status'] == 'Tallied']
        
        stats = {
            'matched_sms_count': len(matched_sms),
            'matched_tally_count': len(matched_tally),
            'unmatched_sms_count': len(sms_df) - len(matched_sms),
            'unmatched_tally_count': len(tally_df) - len(matched_tally),
            'matched_sms_sum': matched_sms['Amount'].sum(),
            'matched_tally_sum': matched_tally['Amount'].sum(),
            'total_sms_sum': sms_df['Amount'].sum(),
            'total_tally_sum': tally_df['Amount'].sum(),
        }
        
        return stats