import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sheets_connector import DataStore

def verify():
    load_dotenv()
    print("--- Google Sheets Connection Verification ---")
    
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    
    print(f"Credentials Path: {creds_path}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    
    if not creds_path or not os.path.exists(creds_path):
        print("❌ Error: Credentials file not found.")
        return False
        
    try:
        ds = DataStore()
        print("✅ Authorized and connected to spreadsheet.")
        
        # Try fetching one record from each major sheet
        sheets_to_check = [
            "BankAccounts", "Vendors", "Clients", 
            "Payables", "Receivables", "ChequeRegister"
        ]
        
        for sheet_name in sheets_to_check:
            try:
                records = ds._get_all_records(sheet_name)
                print(f"✅ {sheet_name}: Found {len(records)} records.")
            except Exception as e:
                print(f"❌ {sheet_name}: Error - {e}")
                
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = verify()
    if success:
        print("\nAll connection tests passed! 🚀")
        sys.exit(0)
    else:
        print("\nVerification failed. ❌")
        sys.exit(1)
