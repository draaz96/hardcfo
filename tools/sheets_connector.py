import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class DataStore:
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.gc = None
        self.sh = None
        self.connect()

    def connect(self):
        """Connect to Google Sheets using service account credentials."""
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            # Fallback for environment where path might be missing or for testing
            print(f"Warning: Credentials path {self.credentials_path} not found.")
            return

        creds = Credentials.from_service_account_file(self.credentials_path, scopes=self.scopes)
        self.gc = gspread.authorize(creds)
        self.sh = self.gc.open_by_key(self.spreadsheet_id)

    def refresh_connection(self):
        """Refresh the connection to Google Sheets."""
        self.connect()

    def _get_sheet(self, name: str):
        """Get a specific worksheet by name."""
        if not self.sh:
            self.connect()
        return self.sh.worksheet(name)

    def _get_all_records(self, sheet_name: str) -> List[Dict[str, Any]]:
        """Helper to get all records from a sheet as a list of dictionaries."""
        try:
            sheet = self._get_sheet(sheet_name)
            return sheet.get_all_records()
        except Exception as e:
            print(f"Error reading sheet {sheet_name}: {e}")
            return []

    # --- Read Methods ---

    def get_all_bank_accounts(self) -> List[Dict[str, Any]]:
        return self._get_all_records("BankAccounts")

    def get_all_vendors(self) -> List[Dict[str, Any]]:
        return self._get_all_records("Vendors")

    def get_all_clients(self) -> List[Dict[str, Any]]:
        return self._get_all_records("Clients")

    def get_all_payables(self) -> List[Dict[str, Any]]:
        return self._get_all_records("Payables")

    def get_all_receivables(self) -> List[Dict[str, Any]]:
        return self._get_all_records("Receivables")

    def get_cheque_register(self) -> List[Dict[str, Any]]:
        return self._get_all_records("ChequeRegister")

    # --- Filtered Reads ---

    def get_vendor_by_id(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        vendors = self.get_all_vendors()
        for v in vendors:
            if str(v.get("vendor_id")) == vendor_id:
                return v
        return None

    def get_client_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        clients = self.get_all_clients()
        for c in clients:
            if str(c.get("client_id")) == client_id:
                return c
        return None

    def get_payables_by_status(self, status: str) -> List[Dict[str, Any]]:
        payables = self.get_all_payables()
        return [p for p in payables if p.get("status") == status]

    def get_receivables_by_status(self, status: str) -> List[Dict[str, Any]]:
        receivables = self.get_all_receivables()
        return [r for r in receivables if r.get("status") == status]

    # --- Write Methods ---

    def add_payable(self, data: Dict[str, Any]) -> bool:
        try:
            sheet = self._get_sheet("Payables")
            # Assumes data keys match header names exactly
            headers = sheet.row_values(1)
            row = [data.get(header, "") for header in headers]
            sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding payable: {e}")
            return False

    def add_receivable(self, data: Dict[str, Any]) -> bool:
        try:
            sheet = self._get_sheet("Receivables")
            headers = sheet.row_values(1)
            row = [data.get(header, "") for header in headers]
            sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding receivable: {e}")
            return False

    def update_payable(self, invoice_id: str, updates: Dict[str, Any]) -> bool:
        try:
            sheet = self._get_sheet("Payables")
            records = sheet.get_all_records()
            for i, record in enumerate(records):
                if str(record.get("invoice_id")) == invoice_id:
                    # Found the row (gspread uses 1-based indexing, header is 1)
                    row_index = i + 2 
                    # Get headers to map keys to columns
                    headers = sheet.row_values(1)
                    for key, value in updates.items():
                        if key in headers:
                            col_index = headers.index(key) + 1
                            sheet.update_cell(row_index, col_index, value)
                    return True
            return False
        except Exception as e:
            print(f"Error updating payable: {e}")
            return False

    def update_receivable(self, invoice_id: str, updates: Dict[str, Any]) -> bool:
        try:
            sheet = self._get_sheet("Receivables")
            records = sheet.get_all_records()
            for i, record in enumerate(records):
                if str(record.get("invoice_id")) == invoice_id:
                    row_index = i + 2
                    headers = sheet.row_values(1)
                    for key, value in updates.items():
                        if key in headers:
                            col_index = headers.index(key) + 1
                            sheet.update_cell(row_index, col_index, value)
                    return True
            return False
        except Exception as e:
            print(f"Error updating receivable: {e}")
            return False

    # --- Utility ---

    def get_last_updated(self, sheet_name: str) -> Optional[datetime]:
        """In a real scenario, this might look at a specific 'Last Updated' cell or sheet metadata."""
        # Simple placeholder approach: return current time
        return datetime.now()
