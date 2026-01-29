import os
import json
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.sheets_connector import DataStore as SheetsConnector
from tools.data_store import DataStore as JSONDataStore

def sync():
    load_dotenv()
    print("--- Synchronizing Google Sheets to database.json ---")
    
    try:
        sheets = SheetsConnector()
        json_db = JSONDataStore()
        
        # 1. Fetch data from Sheets
        print("Fetching data from Google Sheets...")
        bank_accounts = sheets.get_all_bank_accounts()
        vendors = sheets.get_all_vendors()
        clients = sheets.get_all_clients()
        payables = sheets.get_all_payables()
        receivables = sheets.get_all_receivables()
        cheques = sheets.get_cheque_register()
        
        # 2. Update the JSON structure
        # The structure expected by data_store.py needs to match database.json
        new_data = {
            "company": json_db.data.get("company", {}), # Keep existing company info
            "bank_accounts": bank_accounts,
            "vendors": vendors,
            "clients": clients,
            "projects": json_db.data.get("projects", []), # Sheets might not have projects yet
            "payables": payables,
            "receivables": receivables,
            "cheque_register": cheques,
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "source": "Google Sheets Sync"
            }
        }
        
        # 3. Save to database.json
        print(f"Saving to {json_db.db_path}...")
        with open(json_db.db_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False, default=str)
            
        print("✅ Sync completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return False

if __name__ == "__main__":
    if sync():
        sys.exit(0)
    else:
        sys.exit(1)
